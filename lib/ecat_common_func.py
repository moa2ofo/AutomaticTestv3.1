"""EtherCAT master dedicato alla comunicazione CoE/SDO.

Il mapping PDO viene comunque letto e configurato tramite ``config_map()``, ma
l'applicazione non esegue uno scambio PDO ciclico e non porta automaticamente
la rete in OP. Lo stato operativo predefinito e' SAFE-OP, nel quale il mailbox
CoE/SDO resta disponibile e la configurazione PDO e' gia stata validata.
"""

from __future__ import annotations

import struct
import time
from dataclasses import dataclass
from typing import Any, Callable, ClassVar
import pysoem


ETHERCAT_STATES = {
    pysoem.INIT_STATE: "INIT",
    pysoem.PREOP_STATE: "PRE-OP",
    pysoem.SAFEOP_STATE: "SAFE-OP",
    pysoem.OP_STATE: "OPERATIONAL",
}


DEFAULT_INTERFACE = r"\Device\NPF_{8B8E55E1-1E21-450D-9E52-FEAF245CCC3A}"


@dataclass(frozen=True)
class PdoEntry:
    index: int
    subindex: int
    bit_length: int

    @classmethod
    def from_mapping_value(cls, value: int) -> "PdoEntry":
        return cls(
            index=(value >> 16) & 0xFFFF,
            subindex=(value >> 8) & 0xFF,
            bit_length=value & 0xFF,
        )


@dataclass(frozen=True)
class PdoMapping:
    direction: str
    assignment_index: int
    mapping_index: int
    entries: tuple[PdoEntry, ...]


class EthercatSdoMaster:
    """Master EtherCAT per accessi SDO con mapping PDO abilitato."""

    _ENCODERS: ClassVar[dict[str, Callable[[Any], bytes]]] = {
        "BOOLEAN": lambda value: bytes((1 if value else 0,)),
        "INTEGER8": lambda value: struct.pack("<b", value),
        "INTEGER16": lambda value: struct.pack("<h", value),
        "INTEGER32": lambda value: struct.pack("<i", value),
        "INTEGER64": lambda value: struct.pack("<q", value),
        "UNSIGNED8": lambda value: struct.pack("<B", value),
        "UNSIGNED16": lambda value: struct.pack("<H", value),
        "UNSIGNED32": lambda value: struct.pack("<I", value),
        "UNSIGNED64": lambda value: struct.pack("<Q", value),
        "REAL32": lambda value: struct.pack("<f", value),
        "REAL64": lambda value: struct.pack("<d", value),
        "VISIBLE_STRING": lambda value: str(value).encode("utf-8") + b"\x00",
        "OCTET_STRING": bytes,
    }

    _DECODERS: ClassVar[dict[str, Callable[[bytes], Any]]] = {
        "BOOLEAN": lambda data: bool(data[0]),
        "INTEGER8": lambda data: struct.unpack("<b", data[:1])[0],
        "INTEGER16": lambda data: struct.unpack("<h", data[:2])[0],
        "INTEGER32": lambda data: struct.unpack("<i", data[:4])[0],
        "INTEGER64": lambda data: struct.unpack("<q", data[:8])[0],
        "UNSIGNED8": lambda data: struct.unpack("<B", data[:1])[0],
        "UNSIGNED16": lambda data: struct.unpack("<H", data[:2])[0],
        "UNSIGNED32": lambda data: struct.unpack("<I", data[:4])[0],
        "UNSIGNED64": lambda data: struct.unpack("<Q", data[:8])[0],
        "REAL32": lambda data: struct.unpack("<f", data[:4])[0],
        "REAL64": lambda data: struct.unpack("<d", data[:8])[0],
        "VISIBLE_STRING": lambda data: data.split(b"\x00", 1)[0].decode(
            "utf-8", errors="replace"
        ),
        "OCTET_STRING": lambda data: data,
    }

    def __init__(
        self,
        interface_name: str = DEFAULT_INTERFACE,
        *,
        scan_attempts: int = 100,
        scan_delay_s: float = 0.2,
        state_timeout_us: int = 5_000_000,
        map_pdos: bool = True,
        request_safeop: bool = True,
    ) -> None:
        self.interface_name = interface_name
        self.scan_attempts = scan_attempts
        self.scan_delay_s = scan_delay_s
        self.state_timeout_us = state_timeout_us
        self.map_pdos = map_pdos
        self.request_safeop = request_safeop

        self.master = pysoem.Master()
        self._is_open = False
        self.io_map_size = 0

    def connect(self) -> None:
        """Apre l'interfaccia, trova gli slave e prepara il mapping PDO."""
        if self._is_open:
            return

        try:
            self.master.open(self.interface_name)
            self._is_open = True
            self._discover_slaves()
            self._print_slave_identities()

            self.configure_pdos()


            self.print_all_pdo_mappings()
            self._request_state(pysoem.PREOP_STATE, "PRE-OP")
        except Exception:
            self.close()
            raise

    def configure_pdos(self) -> None:
        print("\n========== PDO CONFIGURATION ==========")

        try:
            self.io_map_size = self.master.config_map()

        except pysoem.ConfigMapError as exc:
            print("[ERROR] config_map() failed")

            errors = getattr(exc, "error_list", [])

            if not errors:
                print(f"[ERROR] {exc!r}")

            for number, error in enumerate(errors, start=1):
                print(f"[ERROR {number}] type={type(error).__name__}")

                for attribute in (
                    "slave_pos",
                    "index",
                    "subindex",
                    "abort_code",
                    "error_code",
                    "desc",
                    "message",
                ):
                    if hasattr(error, attribute):
                        value = getattr(error, attribute)

                        if attribute in {
                            "index",
                            "abort_code",
                            "error_code",
                        } and isinstance(value, int):
                            value = f"0x{value:08X}"

                        print(f"    {attribute}: {value}")

            raise

        print(f"[INFO] IO map size: {self.io_map_size} byte")

        for index, slave in enumerate(self.master.slaves):
            print(
                f"[{index}] {slave.name}: "
                f"output/RxPDO={len(slave.output)} byte, "
                f"input/TxPDO={len(slave.input)} byte"
            )

        if self.io_map_size == 0:
            raise RuntimeError(
                "config_map() completed but generated an empty IO map."
            )

    def print_ethercat_state(self) -> None:
        self.master.read_state()

        for index, slave in enumerate(self.master.slaves):
            raw_state = slave.state
            base_state = raw_state & 0x0F
            has_error = bool(raw_state & pysoem.STATE_ERROR)

            state_name = ETHERCAT_STATES.get(
                base_state,
                f"UNKNOWN 0x{base_state:02X}",
            )

            al_status = getattr(slave, "al_status", 0)

            try:
                al_text = pysoem.al_status_code_to_string(al_status)
            except Exception:
                al_text = "Unknown AL status"

            print(
                f"[{index}] {slave.name}: "
                f"state={state_name}, "
                f"raw=0x{raw_state:02X}, "
                f"error={has_error}, "
                f"AL=0x{al_status:04X} ({al_text})"
            )

    def close(self) -> None:
        """Riporta la rete in INIT e chiude l'interfaccia."""
        if not self._is_open:
            return

        try:
            self.master.state = pysoem.INIT_STATE
            self.master.write_state()
        finally:
            self.master.close()
            self._is_open = False

    def __enter__(self) -> "EthercatSdoMaster":
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def _discover_slaves(self) -> None:
        for attempt in range(1, self.scan_attempts + 1):
            slave_count = self.master.config_init()
            if slave_count > 0:
                print(f"Slave trovati: {slave_count}")
                return

            if attempt < self.scan_attempts:
                time.sleep(self.scan_delay_s)

        raise RuntimeError(
            f"Nessuno slave trovato dopo {self.scan_attempts} tentativi "
            f"sull'interfaccia {self.interface_name!r}"
        )

    def _print_slave_identities(self) -> None:
        for position, slave in enumerate(self.master.slaves):
            print(
                f"[{position}] {slave.name} | vendor=0x{slave.man:08X} "
                f"product=0x{slave.id:08X} revision=0x{slave.rev:08X}"
            )

    def _request_state(self, state: int, label: str) -> None:
        self.master.state = state
        self.master.write_state()
        reached = self.master.state_check(state, self.state_timeout_us)
        if reached != state:
            self._raise_state_error(label)
        print(f"Master in {label}")

    def _enter_safeop(self) -> None:
        """Entra in SAFE-OP senza avviare un ciclo PDO continuo."""
        self.master.state = pysoem.SAFEOP_STATE
        self.master.write_state()

        # Un breve scambio di process data puo' essere necessario per completare
        # la transizione dopo config_map(). Non viene mantenuto alcun ciclo PDO.
        if self.map_pdos:
            for _ in range(10):
                self.master.send_processdata()
                self.master.receive_processdata(2_000)
                if (
                    self.master.state_check(pysoem.SAFEOP_STATE, 50_000)
                    == pysoem.SAFEOP_STATE
                ):
                    break

        reached = self.master.state_check(
            pysoem.SAFEOP_STATE, self.state_timeout_us
        )
        if reached != pysoem.SAFEOP_STATE:
            self._raise_state_error("SAFE-OP")
        print("Master in SAFE-OP; comunicazione applicativa solo via SDO")

    def _raise_state_error(self, requested_label: str) -> None:
        self.master.read_state()
        details: list[str] = []
        for position, slave in enumerate(self.master.slaves):
            al_status = getattr(slave, "al_status", 0)
            try:
                al_text = pysoem.al_status_code_to_string(al_status)
            except Exception:
                al_text = "stato AL non disponibile"
            details.append(
                f"slave {position} ({slave.name}): state=0x{slave.state:02X}, "
                f"AL=0x{al_status:04X} ({al_text})"
            )
        raise RuntimeError(
            f"Impossibile raggiungere {requested_label}. " + "; ".join(details)
        )

    def _slave(self, slave_index: int):
        if not self._is_open:
            raise RuntimeError("Master non connesso")
        try:
            return self.master.slaves[slave_index]
        except IndexError as exc:
            raise IndexError(f"Indice slave non valido: {slave_index}") from exc

    @staticmethod
    def _read_u8(slave: Any, index: int, subindex: int) -> int:
        data = slave.sdo_read(index, subindex)
        if not data:
            raise ValueError(f"Oggetto 0x{index:04X}:{subindex:02X} vuoto")
        return data[0]

    @staticmethod
    def _read_u16(slave: Any, index: int, subindex: int) -> int:
        data = slave.sdo_read(index, subindex)
        return int.from_bytes(data, "little", signed=False)

    def read_pdo_mappings(self, slave_index: int) -> tuple[PdoMapping, ...]:
        """Legge i PDO assegnati tramite 0x1C12 e 0x1C13 usando SDO."""
        slave = self._slave(slave_index)
        mappings: list[PdoMapping] = []

        assignments = (
            ("RxPDO", 0x1C12),
            ("TxPDO", 0x1C13),
        )

        for direction, assignment_index in assignments:
            try:
                assigned_count = self._read_u8(slave, assignment_index, 0)
            except pysoem.SdoError:
                continue

            for assignment_subindex in range(1, assigned_count + 1):
                mapping_index = self._read_u16(
                    slave, assignment_index, assignment_subindex
                )
                if mapping_index == 0:
                    continue

                entry_count = self._read_u8(slave, mapping_index, 0)
                entries = tuple(
                    PdoEntry.from_mapping_value(
                        int.from_bytes(
                            slave.sdo_read(mapping_index, entry_subindex),
                            "little",
                            signed=False,
                        )
                    )
                    for entry_subindex in range(1, entry_count + 1)
                )
                mappings.append(
                    PdoMapping(
                        direction=direction,
                        assignment_index=assignment_index,
                        mapping_index=mapping_index,
                        entries=entries,
                    )
                )

        return tuple(mappings)

    def print_pdo_mapping(self, slave_index: int) -> None:
        slave = self._slave(slave_index)
        print(f"\n=== PDO map slave {slave_index}: {slave.name} ===")

        try:
            mappings = self.read_pdo_mappings(slave_index)
        except pysoem.SdoError as exc:
            print(f"Lettura mapping PDO fallita: {exc}")
            return

        if not mappings:
            print("Nessun PDO assegnato tramite 0x1C12/0x1C13")
            return

        for mapping in mappings:
            total_bits = sum(entry.bit_length for entry in mapping.entries)
            print(
                f"{mapping.direction} 0x{mapping.mapping_index:04X} "
                f"({len(mapping.entries)} entry, {total_bits} bit)"
            )
            for entry in mapping.entries:
                print(
                    f"  - 0x{entry.index:04X}:{entry.subindex:02X} "
                    f"({entry.bit_length} bit)"
                )

    def print_all_pdo_mappings(self) -> None:
        for slave_index in range(len(self.master.slaves)):
            self.print_pdo_mapping(slave_index)

    @classmethod
    def encode_value(cls, value: Any, data_type: str) -> bytes:
        normalized_type = data_type.upper()
        try:
            return cls._ENCODERS[normalized_type](value)
        except KeyError as exc:
            raise ValueError(f"Tipo CoE non supportato: {data_type}") from exc
        except (TypeError, ValueError, struct.error) as exc:
            raise ValueError(
                f"Valore {value!r} non valido per {normalized_type}"
            ) from exc

    @classmethod
    def decode_value(cls, data: bytes, data_type: str) -> Any:
        normalized_type = data_type.upper()
        try:
            decoder = cls._DECODERS[normalized_type]
        except KeyError as exc:
            raise ValueError(f"Tipo CoE non supportato: {data_type}") from exc

        try:
            return decoder(data)
        except (IndexError, struct.error) as exc:
            raise ValueError(
                f"Dimensione dati non valida per {normalized_type}: {len(data)} byte"
            ) from exc

    def read_sdo(
        self,
        slave_index: int,
        index: int,
        subindex: int = 0,
        data_type: str = "UNSIGNED32",
        *,
        complete_access: bool = False,
    ) -> Any:
        slave = self._slave(slave_index)
        raw = slave.sdo_read(index, subindex, ca=complete_access)
        value = self.decode_value(raw, data_type)
        print(
            f"SDO read slave={slave_index} 0x{index:04X}:{subindex:02X} "
            f"raw={raw.hex()} value={value!r}"
        )
        return value

    def write_sdo(
        self,
        slave_index: int,
        index: int,
        subindex: int,
        value: Any,
        data_type: str = "UNSIGNED32",
        *,
        complete_access: bool = False,
    ) -> None:
        slave = self._slave(slave_index)
        raw = self.encode_value(value, data_type)
        slave.sdo_write(index, subindex, raw, ca=complete_access)
        print(
            f"SDO write slave={slave_index} 0x{index:04X}:{subindex:02X} "
            f"raw={raw.hex()} value={value!r}"
        )

    def reset_cia402_fault(self, slave_index: int = 0) -> bool:
        """Esegue il fault reset CiA 402 tramite soli SDO."""
        statusword = self.read_sdo(
            slave_index, 0x6041, 0, "UNSIGNED16"
        )
        if not statusword & 0x0008:
            print("Nessun fault CiA 402 attivo")
            return False

        self.write_sdo(slave_index, 0x6040, 0, 0x0080, "UNSIGNED16")
        time.sleep(0.1)
        self.write_sdo(slave_index, 0x6040, 0, 0x0000, "UNSIGNED16")
        print("Fault reset CiA 402 inviato via SDO")
        return True

    def print_diagnostics(self) -> None:
        self.master.read_state()
        print("\n========== EtherCAT diagnostics ==========")
        for position, slave in enumerate(self.master.slaves):
            al_status = getattr(slave, "al_status", 0)
            try:
                al_text = pysoem.al_status_code_to_string(al_status)
            except Exception:
                al_text = "n/a"
            print(
                f"[{position}] {slave.name}: state=0x{slave.state:02X}, "
                f"AL=0x{al_status:04X} ({al_text}), "
                f"input={len(slave.input)} byte, output={len(slave.output)} byte"
            )


def main() -> None:
    with EthercatSdoMaster(DEFAULT_INTERFACE) as ethercat:
        ethercat.print_diagnostics()

        # Esempi SDO; adattare gli oggetti al proprio slave.
        statusword = ethercat.read_sdo(0, 0x6041, 0, "UNSIGNED16")
        print(f"Statusword: 0x{statusword:04X}")

        # Abilitare solo se il dispositivo implementa CiA 402.
        # ethercat.reset_cia402_fault(0)


if __name__ == "__main__":
    main()
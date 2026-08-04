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

            # config_init() ha ora popolato master.slaves e i CoE details.
            # Forziamo SOEM a usare letture SDO singole durante config_map().
            self.disable_complete_access_for_config_map()

            self.print_all_pdo_mappings()
            self._request_state(pysoem.PREOP_STATE, "PRE-OP")

            if self.map_pdos:
                self.dump_pdo_configuration(
                    slave_index=0,
                    include_candidate_maps=True,
                )

                self.configure_pdos()
                print("self.configure_pdos()")

            if self.request_safeop:
                print("self._enter_safeop()")
                self._enter_safeop()

        except Exception:
            self.close()
            raise
    def disable_complete_access_for_config_map(self) -> None:
        """
        Impedisce a SOEM di usare letture SDO Complete Access durante
        config_map().

        Utile per slave che dichiarano Complete Access nella SII, ma che
        restituiscono risposte CA non compatibili con SOEM.
        """

        print("\n========== DISABLE COMPLETE ACCESS ==========")

        for position, slave in enumerate(self.master.slaves):
            disable_ca = getattr(slave, "_disable_complete_access", None)

            if disable_ca is None:
                raise RuntimeError(
                    "Questa versione di PySOEM non espone "
                    "CdefSlave._disable_complete_access(). "
                    "È richiesta PySOEM >= 1.1.3."
                )

            disable_ca()

            print(
                f"[INFO] Slave {position} ({slave.name}): "
                "Complete Access disabilitato per config_map()"
            )

        print("=============================================\n")
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
    def dump_pdo_configuration(
    self,
    slave_index: int = 0,
    *,
    include_candidate_maps: bool = True,
) -> None:
        """
        Esegue un dump diagnostico della configurazione PDO EtherCAT.

        Deve essere chiamata in PRE-OP, dopo config_init() e prima di config_map().

        Legge:
        - 0x1C00: Sync Manager Communication Type;
        - 0x1C12: RxPDO assignment;
        - 0x1C13: TxPDO assignment;
        - tutti i mapping PDO assegnati;
        - opzionalmente 0x1600..0x1602 e 0x1A00..0x1A02;
        - informazioni PySOEM disponibili sullo slave;
        - lunghezze raw di ogni risposta SDO.

        Non modifica alcun oggetto dello slave.
        """

        if not self._is_open:
            raise RuntimeError("Master EtherCAT non connesso")

        if not 0 <= slave_index < len(self.master.slaves):
            raise IndexError(
                f"Slave index {slave_index} non valido; "
                f"slave disponibili: {len(self.master.slaves)}"
            )

        slave = self.master.slaves[slave_index]

        def read_raw(index: int, subindex: int) -> bytes | None:
            """
            Legge un oggetto SDO e stampa dimensione, byte raw e valore intero.
            Restituisce None se la lettura fallisce.
            """
            try:
                raw = slave.sdo_read(index, subindex)

                if not isinstance(raw, bytes):
                    raw = bytes(raw)

                value = int.from_bytes(raw, "little", signed=False)

                print(
                    f"  0x{index:04X}:{subindex:02X} "
                    f"len={len(raw):2d} "
                    f"raw={raw.hex(' '):<23} "
                    f"value=0x{value:X}"
                )

                return raw

            except pysoem.SdoError as exc:
                print(
                    f"  0x{index:04X}:{subindex:02X} "
                    f"SDO ERROR: {exc}"
                )
                return None

            except pysoem.MailboxError as exc:
                print(
                    f"  0x{index:04X}:{subindex:02X} "
                    f"MAILBOX ERROR: {exc}"
                )
                return None

            except pysoem.WkcError as exc:
                print(
                    f"  0x{index:04X}:{subindex:02X} "
                    f"WKC ERROR: {exc}"
                )
                return None

            except Exception as exc:
                print(
                    f"  0x{index:04X}:{subindex:02X} "
                    f"{type(exc).__name__}: {exc}"
                )
                return None

        def check_size(
            index: int,
            subindex: int,
            raw: bytes | None,
            expected_size: int,
            type_name: str,
        ) -> bool:
            """
            Verifica che la risposta SDO abbia la dimensione prevista.
            """
            if raw is None:
                return False

            if len(raw) == expected_size:
                print(
                    f"    [OK] {type_name}: "
                    f"{expected_size} byte"
                )
                return True

            print(
                f"    [ERROR] 0x{index:04X}:{subindex:02X}: "
                f"atteso {type_name} da {expected_size} byte, "
                f"ricevuti {len(raw)} byte"
            )
            return False

        def dump_assignment(
            assignment_index: int,
            direction: str,
        ) -> list[int]:
            """
            Legge 0x1C12 o 0x1C13 e restituisce gli indici PDO assegnati.
            """
            print(
                f"\n--- {direction} assignment "
                f"0x{assignment_index:04X} ---"
            )

            assigned_pdos: list[int] = []

            raw_count = read_raw(assignment_index, 0)
            check_size(
                assignment_index,
                0,
                raw_count,
                1,
                "UNSIGNED8",
            )

            if raw_count is None:
                return assigned_pdos

            assigned_count = int.from_bytes(
                raw_count,
                "little",
                signed=False,
            )

            print(f"    PDO assegnati dichiarati: {assigned_count}")

            if assigned_count > 32:
                print(
                    f"    [ERROR] Numero PDO non plausibile: "
                    f"{assigned_count}"
                )
                return assigned_pdos

            for subindex in range(1, assigned_count + 1):
                raw = read_raw(assignment_index, subindex)

                size_ok = check_size(
                    assignment_index,
                    subindex,
                    raw,
                    2,
                    "UNSIGNED16",
                )

                if raw is None:
                    continue

                pdo_index = int.from_bytes(
                    raw,
                    "little",
                    signed=False,
                )

                assigned_pdos.append(pdo_index)

                if not size_ok:
                    print(
                        f"    [SUSPECT] Assignment 0x{pdo_index:04X} "
                        "restituito con dimensione errata"
                    )

                if not (
                    0x1600 <= pdo_index <= 0x17FF
                    or 0x1A00 <= pdo_index <= 0x1BFF
                ):
                    print(
                        f"    [WARN] Indice PDO non standard: "
                        f"0x{pdo_index:04X}"
                    )

            return assigned_pdos

        def dump_mapping(
            mapping_index: int,
            direction: str,
        ) -> tuple[int, int]:
            """
            Legge un mapping PDO.

            Returns:
                tuple:
                    numero di entry valide;
                    numero totale di bit dichiarati.
            """
            print(
                f"\n--- {direction} mapping "
                f"0x{mapping_index:04X} ---"
            )

            raw_count = read_raw(mapping_index, 0)
            check_size(
                mapping_index,
                0,
                raw_count,
                1,
                "UNSIGNED8",
            )

            if raw_count is None:
                return 0, 0

            entry_count = int.from_bytes(
                raw_count,
                "little",
                signed=False,
            )

            print(f"    Mapping entry dichiarate: {entry_count}")

            if entry_count > 64:
                print(
                    f"    [ERROR] Numero mapping entry non plausibile: "
                    f"{entry_count}"
                )
                return entry_count, 0

            total_bits = 0

            for subindex in range(1, entry_count + 1):
                raw = read_raw(mapping_index, subindex)

                size_ok = check_size(
                    mapping_index,
                    subindex,
                    raw,
                    4,
                    "UNSIGNED32",
                )

                if raw is None:
                    continue

                mapping_value = int.from_bytes(
                    raw,
                    "little",
                    signed=False,
                )

                object_index = (mapping_value >> 16) & 0xFFFF
                object_subindex = (mapping_value >> 8) & 0xFF
                bit_length = mapping_value & 0xFF

                total_bits += bit_length

                print(
                    f"    -> 0x{object_index:04X}:"
                    f"{object_subindex:02X}, "
                    f"{bit_length} bit"
                )

                if not size_ok:
                    print(
                        "       [SUSPECT] Mapping entry trasferita "
                        "con dimensione diversa da 32 bit"
                    )

                if bit_length == 0:
                    print(
                        "       [ERROR] Mapping entry con lunghezza zero"
                    )

                if object_index == 0:
                    print(
                        f"       [INFO] Padding PDO di "
                        f"{bit_length} bit"
                    )

            total_bytes = (total_bits + 7) // 8

            print(
                f"    Totale: {total_bits} bit, "
                f"{total_bytes} byte"
            )

            if total_bits % 8:
                print(
                    "    [WARN] Il PDO non termina su un confine "
                    "di byte"
                )

            return entry_count, total_bits

        print("\n")
        print("=" * 72)
        print("ETHER​CAT PDO DIAGNOSTIC DUMP")
        print("=" * 72)

        print("\n--- Slave identity ---")
        print(f"Slave index:        {slave_index}")
        print(f"Name:               {slave.name}")
        print(f"Vendor ID:          0x{slave.man:08X}")
        print(f"Product code:       0x{slave.id:08X}")
        print(f"Revision:           0x{slave.rev:08X}")
        print(f"State raw:          0x{slave.state:02X}")
        print(f"AL status:          0x{slave.al_status:04X}")

        try:
            al_text = pysoem.al_status_code_to_string(slave.al_status)
        except Exception:
            al_text = "n/a"

        print(f"AL description:     {al_text}")

        print("\n--- PySOEM process-data information before config_map ---")

        for attribute in (
            "obits",
            "ibits",
            "obytes",
            "ibytes",
            "output",
            "input",
        ):
            try:
                value = getattr(slave, attribute)

                if isinstance(value, bytes):
                    print(
                        f"{attribute:<20} "
                        f"len={len(value)}, raw={value.hex(' ')}"
                    )
                else:
                    print(f"{attribute:<20} {value}")

            except Exception as exc:
                print(
                    f"{attribute:<20} "
                    f"not available ({type(exc).__name__}: {exc})"
                )

        print("\n--- Sync Manager Communication Type 0x1C00 ---")

        raw_sm_count = read_raw(0x1C00, 0)
        check_size(0x1C00, 0, raw_sm_count, 1, "UNSIGNED8")

        if raw_sm_count is not None:
            sm_count = int.from_bytes(
                raw_sm_count,
                "little",
                signed=False,
            )

            print(f"    Sync Manager dichiarati: {sm_count}")

            if sm_count > 16:
                print(
                    f"    [ERROR] Numero Sync Manager non plausibile: "
                    f"{sm_count}"
                )
            else:
                sm_type_names = {
                    0: "unused",
                    1: "mailbox write",
                    2: "mailbox read",
                    3: "process data output / RxPDO",
                    4: "process data input / TxPDO",
                }

                for subindex in range(1, sm_count + 1):
                    raw = read_raw(0x1C00, subindex)
                    check_size(
                        0x1C00,
                        subindex,
                        raw,
                        1,
                        "UNSIGNED8",
                    )

                    if raw is not None:
                        sm_type = int.from_bytes(
                            raw,
                            "little",
                            signed=False,
                        )
                        print(
                            f"    SM{subindex - 1}: "
                            f"{sm_type_names.get(sm_type, 'unknown')} "
                            f"(type={sm_type})"
                        )

        rx_assignments = dump_assignment(
            0x1C12,
            "RxPDO / master-to-slave",
        )

        tx_assignments = dump_assignment(
            0x1C13,
            "TxPDO / slave-to-master",
        )

        print("\n--- Assigned PDO mappings ---")

        rx_total_bits = 0
        tx_total_bits = 0

        for mapping_index in rx_assignments:
            _, bits = dump_mapping(
                mapping_index,
                "RxPDO",
            )
            rx_total_bits += bits

        for mapping_index in tx_assignments:
            _, bits = dump_mapping(
                mapping_index,
                "TxPDO",
            )
            tx_total_bits += bits

        if include_candidate_maps:
            print("\n--- Candidate PDO mapping objects ---")

            already_dumped = set(rx_assignments + tx_assignments)

            candidate_maps = (
                ("RxPDO candidate", 0x1600),
                ("RxPDO candidate", 0x1601),
                ("RxPDO candidate", 0x1602),
                ("TxPDO candidate", 0x1A00),
                ("TxPDO candidate", 0x1A01),
                ("TxPDO candidate", 0x1A02),
            )

            for direction, mapping_index in candidate_maps:
                if mapping_index in already_dumped:
                    continue

                dump_mapping(mapping_index, direction)

        print("\n--- Summary ---")

        print(
            f"RxPDO assignment: "
            f"{', '.join(f'0x{x:04X}' for x in rx_assignments) or 'none'}"
        )
        print(
            f"TxPDO assignment: "
            f"{', '.join(f'0x{x:04X}' for x in tx_assignments) or 'none'}"
        )

        print(
            f"RxPDO total:       {rx_total_bits} bit, "
            f"{(rx_total_bits + 7) // 8} byte"
        )
        print(
            f"TxPDO total:       {tx_total_bits} bit, "
            f"{(tx_total_bits + 7) // 8} byte"
        )

        if rx_total_bits == 56:
            print("[OK] RxPDO attivo misura 7 byte")
        else:
            print(
                f"[WARN] RxPDO attivo non misura 56 bit: "
                f"{rx_total_bits} bit"
            )

        if tx_total_bits == 56:
            print("[OK] TxPDO attivo misura 7 byte")
        else:
            print(
                f"[WARN] TxPDO attivo non misura 56 bit: "
                f"{tx_total_bits} bit"
            )

        print("=" * 72)
        print("END ETHERCAT PDO DIAGNOSTIC DUMP")
        print("=" * 72)
        print()


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
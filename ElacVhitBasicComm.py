# -*- coding: utf-8 -*-
"""Test ELAC via EtherCAT CoE/SDO in PRE-OP, senza IO map PDO."""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Protocol

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import lib.cancommonfunctions as cf
from lib.ecat_common_func import DEFAULT_INTERFACE, EthercatSdoMaster


EXIT_OK: Final = 0
EXIT_INVALID_PARAMETERS: Final = 1
EXIT_ETHERCAT_NOT_READY: Final = 2
EXIT_APPLICATION_ERROR: Final = 3

SLAVE_INDEX: Final = 0
FAULT_RESET_TIMEOUT_S: Final = 5.0
COMMAND_DELAY_S: Final = 0.05


class SupportsSdo(Protocol):
    def upload(self, index: int, subindex: int = 0) -> bytes: ...
    def download(self, index: int, subindex: int, data: bytes) -> None: ...


@dataclass(frozen=True)
class StopController:
    path: Path | None

    @classmethod
    def from_environment(cls) -> "StopController":
        value = os.getenv("STOP_FILE")
        return cls(Path(value) if value else None)

    def print_configuration(self) -> None:
        if self.path:
            print(f"[INFO] STOP_FILE: {self.path}")

    def ensure_not_requested(self) -> None:
        if self.path and self.path.is_file():
            raise InterruptedError("Stop richiesto dalla GUI.")


class SdoEntry:
    def __init__(
        self,
        owner: "RawSdoAdapter",
        index: int,
        subindex: int = 0,
        *,
        signed: bool = False,
        size: int | None = None,
        as_bytes: bool = False,
    ) -> None:
        self.owner = owner
        self.index = index
        self.subindex = subindex
        self.signed = signed
        self.size = size
        self.as_bytes = as_bytes

    @property
    def raw(self) -> Any:
        data = self.owner.upload(self.index, self.subindex)
        return data if self.as_bytes else int.from_bytes(
            data, "little", signed=self.signed
        )

    @raw.setter
    def raw(self, value: Any) -> None:
        if isinstance(value, (bytes, bytearray, memoryview)):
            data = bytes(value)
        elif isinstance(value, str):
            data = value.encode("utf-8") + b"\x00"
        elif isinstance(value, int):
            size = self.size or max(1, (value.bit_length() + 7) // 8)
            data = value.to_bytes(size, "little", signed=self.signed)
        else:
            raise TypeError(f"Unsupported SDO value: {type(value).__name__}")

        self.owner.download(self.index, self.subindex, data)


class SdoDictionary:
    OBJECTS: Final = {
        "controlword": (0x6040, 0, False, 2, False),
        "control word": (0x6040, 0, False, 2, False),
        "statusword": (0x6041, 0, False, 2, False),
        "status word": (0x6041, 0, False, 2, False),
        "modes of operation": (0x6060, 0, True, 1, False),
        "mode of operation": (0x6060, 0, True, 1, False),
        "modes of operation display": (0x6061, 0, True, 1, False),
        "mode of operation display": (0x6061, 0, True, 1, False),
        "software version": (0x100A, 0, False, None, True),
        "manufacturer software version": (0x100A, 0, False, None, True),
        "target velocity": (0x60FF, 0, True, 4, False),
        "target position": (0x607A, 0, True, 4, False),
        "velocity actual value": (0x606C, 0, True, 4, False),
        "position actual value": (0x6064, 0, True, 4, False),
    }

    def __init__(self, owner: "RawSdoAdapter") -> None:
        self.owner = owner

    def upload(self, index: int, subindex: int = 0) -> bytes:
        return self.owner.upload(index, subindex)

    def download(self, index: int, subindex: int, data: bytes) -> None:
        self.owner.download(index, subindex, data)

    read = upload
    write = download

    def __getitem__(self, key: Any) -> SdoEntry:
        if isinstance(key, tuple) and len(key) == 2:
            return SdoEntry(self.owner, int(key[0]), int(key[1]))
        if isinstance(key, int):
            return SdoEntry(self.owner, key)
        if not isinstance(key, str):
            raise KeyError(f"Unsupported SDO key: {key!r}")

        name = " ".join(key.strip().lower().replace("_", " ").split())
        try:
            index, subindex, signed, size, as_bytes = self.OBJECTS[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown SDO object {key!r}; add it to SdoDictionary.OBJECTS."
            ) from exc

        return SdoEntry(
            self.owner,
            index,
            subindex,
            signed=signed,
            size=size,
            as_bytes=as_bytes,
        )


class RawSdoAdapter:
    def __init__(self, ethercat: EthercatSdoMaster, slave_index: int = 0) -> None:
        self.ethercat = ethercat
        self.slave_index = slave_index
        self.sdo = SdoDictionary(self)

    @property
    def slave(self):
        return self.ethercat.master.slaves[self.slave_index]

    @property
    def name(self) -> str:
        return self.slave.name

    def upload(self, index: int, subindex: int = 0) -> bytes:
        return self.slave.sdo_read(index, subindex)

    def download(self, index: int, subindex: int, data: bytes) -> None:
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError("SDO download data must be bytes-like")
        self.slave.sdo_write(index, subindex, bytes(data))

    read = upload
    write = download


@dataclass
class EthercatSession:
    master: EthercatSdoMaster
    drive: RawSdoAdapter

    def close(self) -> None:
        self.master.close()


class EthercatInitializationError(RuntimeError):
    pass


def initialize_ethercat(
    interface_name: str = DEFAULT_INTERFACE,
    slave_index: int = SLAVE_INDEX,
) -> EthercatSession:
    print(f"[INFO] Initializing EtherCAT on {interface_name!r}...")

    ethercat = EthercatSdoMaster(
        interface_name,
        map_pdos=False,
        request_safeop=False,
    )

    try:
        ethercat.connect()

        if not 0 <= slave_index < len(ethercat.master.slaves):
            raise EthercatInitializationError(
                f"Slave index {slave_index} unavailable; "
                f"detected: {len(ethercat.master.slaves)}."
            )

        ethercat.print_diagnostics()

    except Exception as exc:
        ethercat.close()
        if isinstance(exc, EthercatInitializationError):
            raise
        raise EthercatInitializationError(
            "EtherCAT initialization failed. Check interface, hardware, "
            "EEPROM, mailbox CoE and slave state."
        ) from exc

    print("[INFO] EtherCAT ready in PRE-OP; application communication is SDO-only.")
    return EthercatSession(ethercat, RawSdoAdapter(ethercat, slave_index))


def execute_drive_sequence(drive: SupportsSdo, stop: StopController) -> None:
    stop.ensure_not_requested()
    time.sleep(COMMAND_DELAY_S)

    print("[INFO] Clearing drive fault condition via SDO...")
    if cf.QuitFromFaultCondition(
        drive, deadline_s=FAULT_RESET_TIMEOUT_S
    ) is False:
        raise RuntimeError("Unable to clear drive fault condition.")

    stop.ensure_not_requested()
    time.sleep(COMMAND_DELAY_S)

    print("[INFO] Reading software version via SDO...")
    software_version = cf.read_software_version(drive)

    stop.ensure_not_requested()
    print("[INFO] Reading statusword via SDO...")
    statusword = cf.get_sw(drive)

    print(f"[INFO] Statusword: 0x{statusword:04X}")
    print(f"[INFO] Software version: {software_version!r}")

    stop.ensure_not_requested()
    print("[INFO] Resetting drive via SDO...")

    if cf.reset_drive(drive) is False:
        statusword = cf.get_sw(drive)
        raise RuntimeError(
            f"Drive reset failed. Statusword after reset: 0x{statusword:04X}"
        )

    print("[INFO] Drive sequence completed successfully.")


def main() -> int:
    session: EthercatSession | None = None
    stop = StopController.from_environment()
    stop.print_configuration()

    try:
        stop.ensure_not_requested()
        session = initialize_ethercat()
        session.master.print_ethercat_state()
        execute_drive_sequence(session.drive, stop)
        return EXIT_OK

    except InterruptedError as exc:
        print(f"[INFO] {exc}")
        return EXIT_OK
    except ValueError as exc:
        print(f"[ERROR] Invalid parameter or SDO value: {exc}")
        return EXIT_INVALID_PARAMETERS
    except EthercatInitializationError as exc:
        print(f"[ERROR] {exc}")
        if exc.__cause__:
            print(
                f"[ERROR] Cause: {type(exc.__cause__).__name__}: "
                f"{exc.__cause__}"
            )
        print(
            "[STOP] Fix EtherCAT interface, hardware, EEPROM, mailbox CoE "
            "or slave state before running the CiA 402 test."
        )
        return EXIT_ETHERCAT_NOT_READY
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return EXIT_APPLICATION_ERROR
    except KeyboardInterrupt:
        print("\n[INFO] Execution interrupted by user.")
        return EXIT_OK
    except Exception as exc:
        print(f"[ERROR] Unexpected {type(exc).__name__}: {exc}")
        return EXIT_APPLICATION_ERROR
    finally:
        if session:
            try:
                session.close()
            except Exception as exc:
                print(f"[WARN] Error while closing EtherCAT interface: {exc!r}")


if __name__ == "__main__":
    sys.exit(main())
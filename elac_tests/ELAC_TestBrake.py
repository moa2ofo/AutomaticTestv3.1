import time


IDX_BRAKE_OVERLOAD = 0x2024
IDX_BRAKE_COMMAND = 0x2025
IDX_BRAKE_STATUS = 0x2026


def sdo_write_u32(elac, index, subindex, value):
    elac.sdo.download(
        index,
        subindex,
        int(value).to_bytes(4, "little", signed=False)
    )


def sdo_read_u32(elac, index, subindex):
    data = elac.sdo.upload(index, subindex)
    return int.from_bytes(data, "little", signed=False)


def run_brake_test(elac, overload ,command):
    command = int(command)

    print("\033[32mBegin Brake Test\033[0m")

    if overload is not None:
        overload = int(overload)

        sdo_write_u32(elac, IDX_BRAKE_OVERLOAD, 0, overload)
        time.sleep(0.1)

        overload_read = sdo_read_u32(elac, IDX_BRAKE_OVERLOAD, 0)
        print(
            f"[INFO] 0x2024 BrakeOverload scritto={overload}, "
            f"letto={overload_read}"
        )

    sdo_write_u32(elac, IDX_BRAKE_COMMAND, 0, command)
    time.sleep(0.2)

    command_read = sdo_read_u32(elac, IDX_BRAKE_COMMAND, 0)
    print(
        f"[INFO] 0x2025 BrakeCommand scritto={command}, "
        f"letto={command_read}"
    )

    status = sdo_read_u32(elac, IDX_BRAKE_STATUS, 0)
    print(f"[INFO] 0x2026 BrakeStatus = {status}")

    if status == 0:
        print("[INFO] Freno rilasciato")
    elif status == 1:
        print("[INFO] Freno applicato")
    else:
        print(f"[WARN] Stato freno sconosciuto: {status}")

    print("\033[32mBrake Test completed\033[0m")
    return True
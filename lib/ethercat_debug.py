import pysoem
import time

def ethercat_debug(master, iface, io_map_bytes=4096, timeout_s=5.0):
    print("\n========== EtherCAT DEBUG ==========")

    master.open(iface)

    n = master.config_init()
    print(f"Slaves found: {n}")
    if n <= 0:
        print("❌ No slaves found!")
        master.close()
        return False

    # Print identity for all slaves
    print("\n--- Slave Identity (EEPROM/SII) ---")
    for i, s in enumerate(master.slaves):
        print(f"[{i}] Name={s.name} man={hex(s.man)} id={hex(s.id)} rev={hex(s.rev)}")
        if s.man == 0xffffffff or s.id == 0xffffffff:
            print(f"❌ Slave {i} EEPROM/SII not readable")
            master.close()
            return False

    # Map process data (important for OP with multiple slaves)
    io_map = bytearray(io_map_bytes)
    master.config_map(io_map)

    # Optional: distributed clocks config (if you use DC slaves)
    master.config_dc()

    # Go SAFEOP
    master.state = pysoem.SAFEOP_STATE
    master.write_state()

    t0 = time.time()
    while time.time() - t0 < timeout_s:
        master.read_state()
        if all(s.state == pysoem.SAFEOP_STATE for s in master.slaves):
            break
        time.sleep(0.05)

    if not all(s.state == pysoem.SAFEOP_STATE for s in master.slaves):
        print("❌ Not all slaves reached SAFEOP")
        for i, s in enumerate(master.slaves):
            if s.state != pysoem.SAFEOP_STATE:
                print(f"  Slave {i} state={s.state} AL={hex(s.al_status)}")
        master.close()
        return False

    # Go OP
    master.state = pysoem.OP_STATE
    master.write_state()

    t0 = time.time()
    while time.time() - t0 < timeout_s:
        master.read_state()
        if all(s.state == pysoem.OP_STATE for s in master.slaves):
            break
        time.sleep(0.05)

    if not all(s.state == pysoem.OP_STATE for s in master.slaves):
        print("❌ Not all slaves reached OP")
        for i, s in enumerate(master.slaves):
            if s.state != pysoem.OP_STATE:
                print(f"  Slave {i} state={s.state} AL={hex(s.al_status)}")
        master.close()
        return False

    print("\n✅ All slaves reached OP successfully!")

    # WKC check
    master.send_processdata()
    wkc = master.receive_processdata(2000)
    print("Working Counter (WKC):", wkc)

    if wkc == 0:
        print("❌ WKC = 0 → frames not returning")
        master.close()
        return False

    print("✅ EtherCAT cyclic exchange OK!")
    return True
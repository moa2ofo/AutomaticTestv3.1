import pysoem
import time


def ethercat_debug(master):
    print("\n========== EtherCAT DEBUG ==========")

    if master.slavecount == 0:
        print("❌ No slaves found!")
        return False

    slave = master.slaves[0]

    print("\n--- Slave Identity (EEPROM/SII) ---")
    print("Name       :", slave.name)
    print("Vendor ID  :", hex(slave.man))
    print("Product ID :", hex(slave.id))
    print("Revision   :", hex(slave.rev))

    if slave.man == 0xffffffff or slave.id == 0xffffffff:
        print("\n❌ EEPROM/SII NOT READABLE → hardware/EEPROM problem!")
        return False

    print("\n--- Slave State ---")
    print("Initial State:", slave.state)

    # Request SAFE-OP
    master.state = pysoem.SAFEOP_STATE
    master.write_state()

    time.sleep(0.2)
    master.read_state()

    print("After SAFEOP request:", slave.state)

    if slave.state != pysoem.SAFEOP_STATE:
        print("❌ Slave did not reach SAFEOP")
        print("AL Status Code:", hex(slave.al_status))
        return False

    # Request OP
    master.state = pysoem.OP_STATE
    master.write_state()

    time.sleep(0.2)
    master.read_state()

    print("After OP request:", slave.state)

    if slave.state != pysoem.OP_STATE:
        print("❌ Slave did not reach OP")
        print("AL Status Code:", hex(slave.al_status))
        return False

    print("\n✅ Slave reached OP successfully!")

    print("\n--- WKC Check ---")
    wkc = master.send_processdata()
    wkc = master.receive_processdata(2000)

    print("Working Counter (WKC):", wkc)

    if wkc == 0:
        print("❌ WKC = 0 → frames not returning (PHY/magnetics issue)")
        return False

    print("✅ EtherCAT cyclic exchange OK!")
    return True

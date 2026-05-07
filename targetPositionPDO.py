import pysoem
import struct
import time

IFNAME = r'\Device\NPF_{FA39BC94-2EDC-4827-9482-10BD0183CDFA}'

# RxPDO offsets
CTRL_OFS = 0
POS_OFS  = 2
MODE_OFS = 6

MODE_CSP = 8


def main():
    master = pysoem.Master()
    master.open(IFNAME)

    if master.config_init() <= 0:
        raise RuntimeError("No slaves found")

    slave = master.slaves[0]
    print("Slave:", slave.name)

    # ✅ Overlap map (chiave!)
    io_size = master.config_overlap_map()
    print("Overlap IO size:", io_size)

    # SAFE-OP
    master.state = pysoem.SAFEOP_STATE
    master.write_state()

    for _ in range(100):
        master.send_overlap_processdata()
        master.receive_processdata(1000)

    master.state_check(pysoem.SAFEOP_STATE, 5000)
    print("SAFE-OP reached")

    # OPERATIONAL
    master.state = pysoem.OP_STATE
    master.write_state()
    master.state_check(pysoem.OP_STATE, 5000)
    print("OPERATIONAL reached")

    # -------------------------
    # Inizializzazione PDO
    # -------------------------
    struct.pack_into("<b", slave.output, MODE_OFS, MODE_CSP)
    struct.pack_into("<H", slave.output, CTRL_OFS, 0x000F)
    struct.pack_into("<i", slave.output, POS_OFS, 0)

    master.send_overlap_processdata()
    master.receive_processdata(2000)

    print("Drive pronto (PDO overlap mode)")

    try:
        pos = 0
        while True:
            pos += 1000
            struct.pack_into("<i", slave.output, POS_OFS, pos)

            master.send_overlap_processdata()
            master.receive_processdata(2000)
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping")

    # Stop drive
    struct.pack_into("<H", slave.output, CTRL_OFS, 0x0006)
    master.send_overlap_processdata()
    master.receive_processdata(2000)

    master.close()


if __name__ == "__main__":
    main()

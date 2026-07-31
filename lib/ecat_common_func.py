import time
import pysoem
import struct
from .eth_wrapper import EtherCATNode
ifname = r'\Device\NPF_{4CDA18E5-502B-482C-A272-78CDB45D4C0B}'
#ifname = r'\Device\NPF_{8B8E55E1-1E21-450D-9E52-FEAF245CCC3A}'
def dump_sii_mailbox(slave):
    print("\n--- SII Mailbox Info ---")

    # L’offset della categoria è memorizzato nella tabella categorie
    # Leggiamo i primi 64 byte della EEPROM dove c’è la Category Table
    data = slave.eeprom_read(0x40, 64)

    # Ogni entry: [CategoryID(16bit), Length(16bit)]
    # Cerchiamo la categoria 0x000A (Mailbox)
    for i in range(0, 64, 4):
        cat = int.from_bytes(data[i:i+2], "little")
        length = int.from_bytes(data[i+2:i+4], "little")

        if cat == 0x000A:
            offset = 0x40 + i + 4
            size = length * 2  # lunghezza in WORD, converti in byte
            raw = slave.eeprom_read(offset, size)

            # Formato SII Mailbox (standard ETG2010):
            # Word0 = MailboxOutStart
            # Word1 = MailboxOutSize
            # Word2 = MailboxInStart
            # Word3 = MailboxInSize
            # Word4 = SupportedProtocols
            mo_start = int.from_bytes(raw[0:2], "little")
            mo_size  = int.from_bytes(raw[2:4], "little")
            mi_start = int.from_bytes(raw[4:6], "little")
            mi_size  = int.from_bytes(raw[6:8], "little")
            proto = int.from_bytes(raw[8:10], "little")

            print(f"Mailbox-Out Start : 0x{mo_start:04X}")
            print(f"Mailbox-Out Size  : {mo_size} bytes")
            print(f"Mailbox-In Start  : 0x{mi_start:04X}")
            print(f"Mailbox-In Size   : {mi_size} bytes")
            print(f"Protocols (bitmask): 0x{proto:04X}")
            return
    
    print("Mailbox category (0x0A) not found in SII.")
def dump_pdo_via_sdo(slave):
    print(f"\n--- DUMPING PDO via SDO ---\n=== PDO MAP for {slave.name} ===")

    # RX PDO
    for pdo_idx in range(0x1600, 0x1604):
        try:
            n = slave.sdo_read(pdo_idx, 0)[0]
        except Exception:
            continue

        print(f"\nRxPDO 0x{pdo_idx:04X} ({n} entries):")
        for si in range(1, n + 1):
            raw = int.from_bytes(slave.sdo_read(pdo_idx, si), "little")
            index = (raw >> 16) & 0xFFFF
            subidx = (raw >> 8) & 0xFF
            bitlen = raw & 0xFF
            print(f"  - 0x{index:04X}:{subidx}  ({bitlen} bits)")

    # TX PDO
    for pdo_idx in range(0x1A00, 0x1A04):
        try:
            n = slave.sdo_read(pdo_idx, 0)[0]
        except Exception:
            continue

        print(f"\nTxPDO 0x{pdo_idx:04X} ({n} entries):")
        for si in range(1, n + 1):
            raw = int.from_bytes(slave.sdo_read(pdo_idx, si), "little")
            index = (raw >> 16) & 0xFFFF
            subidx = (raw >> 8) & 0xFF
            bitlen = raw & 0xFF
            print(f"  - 0x{index:04X}:{subidx}  ({bitlen} bits))")


class RpPysoem:
    def ethercat_debug(self):
        master = self.master
        print("\n========== EtherCAT DEBUG ==========")
        
        master.send_processdata()
        wkc = master.receive_processdata(2000)
        print("WKC:", wkc)

        n = len(master.slaves)
        print("Slaves len(master.slaves) =", n)
        if n == 0:
            print("❌ No slaves found!")
            return False
    
        s = master.slaves[0]
    
        # Identity (SII)
        print("\n--- Slave Identity (EEPROM/SII) ---")
        print("Name       :", getattr(s, "name", "<no name>"))
        print("Vendor ID  :", hex(getattr(s, "man", 0)))
        print("Product ID :", hex(getattr(s, "id", 0)))
        print("Revision   :", hex(getattr(s, "rev", 0)))
    
        if getattr(s, "man", 0) == 0xffffffff or getattr(s, "id", 0) == 0xffffffff:
            print("\n❌ EEPROM/SII NOT READABLE → very likely EEPROM/wiring/WP/power/strap issue")
            # prova anche a leggere lo stato/AL
            master.read_state()
            print("State:", hex(getattr(s, "state", 0)))
            al = getattr(s, "al_status", getattr(s, "al_status_code", 0))
            print("AL status code:", hex(al))
            try:
                print("AL text:", pysoem.al_status_code_to_string(al))
            except Exception:
                pass
            return False
    
        # State / AL
        print("\n--- State / AL ---")
        master.read_state()
        print("State:", hex(getattr(s, "state", 0)))
        al = getattr(s, "al_status", getattr(s, "al_status_code", 0))
        print("AL status code:", hex(al))
        try:
            print("AL text:", pysoem.al_status_code_to_string(al))
        except Exception:
            pass
    
        # WKC check (process data)
        print("\n--- WKC Check ---")
        master.send_processdata()
        wkc = master.receive_processdata(2000)
        print("WKC:", wkc)
        if wkc == 0:
            print("❌ WKC=0 → frames not returning reliably (PHY/magnetics/strap/reset)")
            return False
        
        
        
        print("✅ Basic cyclic exchange seems alive.")
        return True



    def __init__(self, interface_name=ifname):
        print("Interface :", interface_name)
        # Open interface
        self.master = pysoem.Master()
        self.master.open(interface_name)
        print("Interface opened:", interface_name)

        # Scan slaves



        max_attempts = 100  # opzionale
        attempts = 0

        while True:
            if self.master.config_init() > 0:
                break

            attempts += 1
            if attempts >= max_attempts:
                raise RuntimeError("No slave found")

            time.sleep(0.2)


        print(f"Slaves found: {len(self.master.slaves)}")
        for i, s in enumerate(self.master.slaves):
            print(f"[{i}] SII name: {s.name}")

        # Map PDOs
        print("#############################")
        print("\n=== PDO mapping start ===")
        print("#############################")
        self.master.config_map()
        print("#############################")
        print("\n=== PDO mapping results ===")
        print("#############################")
        for i, s in enumerate(self.master.slaves):
            print(f"\nSlave {i}: {s.name}")
            print(len(s.input), len(s.output))
            dump_pdo_via_sdo(s)
            dump_sii_mailbox(s)






        # SAFE-OP
        self.master.state = pysoem.SAFEOP_STATE
        self.master.write_state()
        self.master.state_check(pysoem.SAFEOP_STATE, 5000)
        print("Master in SAFE-OP")

        # Wrap first slave with your EtherCATNode
        self.node = EtherCATNode(self.master, self.master.slaves[0])

        # Check fault via wrapper
        try:
            sw_bytes = self.node.sdo.upload(0x6041, 0)  # Statusword			
            sw = int.from_bytes(sw_bytes, byteorder='little')
            print(f"Statusword = 0x{sw:04X}")
            if sw & 0x08:  # Fault bit
                print("Fault detected, sending Fault Reset")
                self.s60.sdo["Controlword"].raw = 0x80
                time.sleep(0.1)
        except Exception as e:
            print(f"Could not read Statusword: {e}")
       

        # Go to OPERATIONAL
        self.master.state = pysoem.OP_STATE
        self.master.write_state()
        self.master.state_check(pysoem.OP_STATE, 5000)
        print("Master in OP")

        # Read back state safely
        for i, s in enumerate(self.master.slaves):
            print(f"[{i}] state={s.state & 0xFF}")  # masked AL state only

    # -------------------------------------------------------------------------
    # CoE data encoding / decoding helpers
    # -------------------------------------------------------------------------


    def encode_value(self, value, data_type):
        """Encode Python value into EtherCAT-compatible bytes."""
        type_map = {
            'BOOLEAN': lambda v: bytes([1 if v else 0]),
            'INTEGER8': lambda v: struct.pack('<b', v),
            'INTEGER16': lambda v: struct.pack('<h', v),
            'INTEGER32': lambda v: struct.pack('<i', v),
            'INTEGER64': lambda v: struct.pack('<q', v),
            'UNSIGNED8': lambda v: struct.pack('<B', v),
            'UNSIGNED16': lambda v: struct.pack('<H', v),
            'UNSIGNED32': lambda v: struct.pack('<I', v),
            'UNSIGNED64': lambda v: struct.pack('<Q', v),
            'REAL32': lambda v: struct.pack('<f', v),
            'REAL64': lambda v: struct.pack('<d', v),
            'VISIBLE_STRING': lambda v: v.encode('utf-8') + b'\x00',
            'OCTET_STRING': lambda v: bytes(v),
        }

        if data_type not in type_map:
            raise ValueError(f"Unsupported CoE data type: {data_type}")

        return type_map[data_type](value)

    def decode_value(self, data, data_type):
        """Decode EtherCAT bytes into Python value."""
        type_map = {
            'BOOLEAN': lambda d: bool(d[0]),
            'INTEGER8': lambda d: struct.unpack('<b', d[:1])[0],
            'INTEGER16': lambda d: struct.unpack('<h', d[:2])[0],
            'INTEGER32': lambda d: struct.unpack('<i', d[:4])[0],
            'INTEGER64': lambda d: struct.unpack('<q', d[:8])[0],
            'UNSIGNED8': lambda d: struct.unpack('<B', d[:1])[0],
            'UNSIGNED16': lambda d: struct.unpack('<H', d[:2])[0],
            'UNSIGNED32': lambda d: struct.unpack('<I', d[:4])[0],
            'UNSIGNED64': lambda d: struct.unpack('<Q', d[:8])[0],
            'REAL32': lambda d: struct.unpack('<f', d[:4])[0],
            'REAL64': lambda d: struct.unpack('<d', d[:8])[0],
            'VISIBLE_STRING': lambda d: d.split(b'\x00', 1)[0].decode('utf-8', errors='ignore'),
            'OCTET_STRING': lambda d: d,
        }

        if data_type not in type_map:
            raise ValueError(f"Unsupported CoE data type: {data_type}")

        return type_map[data_type](data)

    def go_to_op_state(self, timeout_ms=5000):
        """
        Bring all EtherCAT slaves to OPERATIONAL state.
        Performs process data mapping, DC config (if supported),
        and verifies all slaves reach OP.
        """
        print("\n[INFO] Transitioning all slaves to OPERATIONAL (OP) state...")

        # Configure PDO mapping and DC synchronization (standard sequence)
        self.master.config_map()
        # self.master.config_dc()

        # Request OP state
        self.master.state = pysoem.OP_STATE
        self.master.write_state()

        # Wait until all slaves reach OP or timeout
        if self.master.state_check(pysoem.OP_STATE, timeout_ms) != pysoem.OP_STATE:
            print("[WARN] Not all slaves reached OP within timeout.")
            self.master.read_state()
            for i, s in enumerate(self.master.slaves):
                print(f"[{i}] {s.name} → state={s.state}, AL status=0x{s.al_status_code:04X}")
            raise RuntimeError("Some slaves failed to reach OP state")

        print("[OK] All slaves are now in OPERATIONAL state.")
        self.master.read_state()
        for i, s in enumerate(self.master.slaves):
            print(f"[{i}] {s.name} → state={s.state} (4=OP)")

    # -------------------------------------------------------------------------
    # Example usage: read/write an SDO with automatic encoding/decoding
    # -------------------------------------------------------------------------

    def read_sdo(self, slave_index, index, subindex, data_type="UNSIGNED32"):
        """Read an SDO and decode it automatically."""
        slave = self.master.slaves[slave_index]
        data = slave.sdo_read(index, subindex)      
        print("RAW SDO DATA:", data)
        print("HEX:", data.hex())
        return self.decode_value(data, data_type)

    def write_sdo(self, slave_index, index, subindex, value, data_type="UNSIGNED32"):
        """Encode and write an SDO."""
        slave = self.master.slaves[slave_index]
        encoded = self.encode_value(value, data_type)
        slave.sdo_write(index, subindex, encoded)
        print(f"Wrote {value} ({data_type}) to 0x{index:04X}:{subindex}")


if __name__ == "__main__":
    rpsoem = RpPysoem()


    m = pysoem.Master()
    m.open(r'\Device\NPF_{7F89FC30-3BA0-4D0F-816C-A87E5B58D585}')
    if m.config_init() <= 0:
        raise RuntimeError("no slaves")
    print("slaves:", len(m.slaves))

    # Request SAFE-OP and pump PD *before* state_check
    m.state = pysoem.SAFEOP_STATE
    m.write_state()
    for _ in range(600):
        m.send_processdata()
        m.receive_processdata(1000)
    ok = (m.state_check(pysoem.SAFEOP_STATE, 8000) == pysoem.SAFEOP_STATE)
    print("SAFE-OP ok?", ok)
    m.read_state()
    for i, s in enumerate(m.slaves):
        print(i, s.name, "state=", s.state, "AL=", hex(getattr(s, 'al_status', 0)))
        print('al status code {} ({})'.format(hex(s.al_status),
                                              pysoem.al_status_code_to_string(s.al_status)))
    m.close()





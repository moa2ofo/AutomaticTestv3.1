# ecat/eth_wrapper.py
import pysoem
import time

# --- Helper Function (Added) ---
def _encode_int_or_bytes(value):
    """Encodes an integer value into a 4-byte little-endian bytes object, or returns bytes as-is."""
    if isinstance(value, bytes):
        return value
    if isinstance(value, int):
        # Defaulting to 4 bytes for raw integer downloads.
        # This size should ideally be inferred from the object dictionary entry,
        # but 4 bytes is a common safe guess for raw access if the size isn't known.
        return value.to_bytes(4, "little")
    raise TypeError(f"Cannot encode type {type(value)}. Must be int or bytes.")
# -------------------------------


class EtherCATNode:
    """
    Wraps a PySOEM slave to mimic python-canopen's Node API.
    Provides:
      - node.sdo[0x6041].raw
      - node.sdo['Statusword'].raw
      - node.sdo.upload()/download()
      - node.nmt.state = 'OPERATIONAL'  (mapped to EtherCAT states via master)
    """

    _ALIASES = {
        'Statusword':  0x6041,
        'Controlword': 0x6040,
    }

    def __init__(self, master, slave):
        self.master = master
        self.slave = slave
        self.id = getattr(slave, "config_addr", 0)

    @property
    def sdo(self):
        return _SDOAccess(self.slave, self._ALIASES)

    @property
    def nmt(self):
        return _NMTShim(self.master, self.slave)


# -------------------------------------------------------------------------
# NMT EMULATION (maps CANopen NMT states to EtherCAT states)
# -------------------------------------------------------------------------
class _NMTShim:
    _EC_STATE_INIT    = 0x01
    _EC_STATE_PRE_OP  = 0x02
    _EC_STATE_SAFE_OP = 0x04
    _EC_STATE_OP      = 0x08

    _STATE_MAP = {
        'INIT': _EC_STATE_INIT,
        'PRE-OPERATIONAL': _EC_STATE_PRE_OP,
        'SAFE-OPERATIONAL': _EC_STATE_SAFE_OP,
        'OPERATIONAL': _EC_STATE_OP,
    }

    def __init__(self, master, slave):
        self._master = master
        self._slave = slave

    @property
    def state(self):
        # ✅ stato del singolo slave (non del master)
        st = getattr(self._slave, "state", None)
        for name, value in self._STATE_MAP.items():
            if value == st:
                return name
        return 'UNKNOWN'

    @state.setter
    def state(self, new_state_str):
        if new_state_str not in self._STATE_MAP:
            raise ValueError(f"Invalid state: {new_state_str}")

        target = self._STATE_MAP[new_state_str]

        # ✅ set master state + write + check
        self._master.state = target
        self._master.write_state()

        start_time = time.time()
        timeout = 5.0
        while time.time() - start_time < timeout:
            # check globale: porta anche gli slave
            self._master.state_check(target, timeout=50000)
            if self._master.state == target:
                break
            time.sleep(0.01)

        if self._master.state != target:
            print(f"Warning: Master failed to reach {new_state_str} state.")

# -------------------------------------------------------------------------
# SDO EMULATION
# -------------------------------------------------------------------------

class _SDOAccess:
    def __init__(self, slave, aliases: dict):
        self._slave = slave
        self._aliases = aliases

    def __getitem__(self, key):
        if isinstance(key, str):
            index = self._aliases.get(key)
            if index is None:
                raise KeyError(f"Alias '{key}' not found in SDO aliases.")
        elif isinstance(key, int):
            index = key
        else:
            raise TypeError("SDO key must be int or str")
        return _SDOObject(self._slave, index)

    # --- FIX 1: Added upload method ---
    def upload(self, index, subindex=0):
        """
        Reads (uploads) an SDO value from the slave.
        Returns the raw bytes read from the SDO.
        This fixes the error you were seeing with the upload function.
        """
        return self._slave.sdo_read(index, subindex)

    # --- FIX 1: Added download method (for completeness, based on your test script usage) ---
    def download(self, index, subindex, data):
        """
        Writes (downloads) an SDO value to the slave.
        Data can be an integer or bytes.
        """
        encoded_data = _encode_int_or_bytes(data)
        self._slave.sdo_write(index, subindex, encoded_data)


class _SDOObject:
    def __init__(self, slave, index: int):
        self._slave = slave
        self._index = index

    @property
    def raw(self) -> int:  # defaults to subindex 0
        data = self._slave.sdo_read(self._index, 0)
        return int.from_bytes(data, "little")

    @raw.setter
    def raw(self, value):
        data = _encode_int_or_bytes(value)
        self._slave.sdo_write(self._index, 0, data)

    def __getitem__(self, subindex: int):
        return _SDOSubObject(self._slave, self._index, subindex)


class _SDOSubObject:
    def __init__(self, slave, index: int, subindex: int):
        self._slave = slave
        self._index = index
        self._sub = subindex

    @property
    def raw(self) -> int:
        data = self._slave.sdo_read(self._index, self._sub)
        return int.from_bytes(data, "little")

    @raw.setter
    def raw(self, value):
        data = _encode_int_or_bytes(value)
        # --- FIX 3: Corrected subindex from 0 to self._sub ---
        self._slave.sdo_write(self._index, self._sub, data)
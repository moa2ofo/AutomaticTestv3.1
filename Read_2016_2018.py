"""
Script autonomo per leggere gli oggetti SDO 0x2016, 0x2017 e 0x2018
via EtherCAT e restituire il valore concatenato.

Esecuzione:
    python Read_2016_2018.py

Output principale:
    Valore concatenato: <valore_0x2016><valore_0x2017><valore_0x2018>
"""

import sys
import os
import time
import struct

# Permette l'esecuzione sia dalla cartella progetto sia da altre cartelle.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from lib.ecat_common_func import RpPysoem
import lib.cancommonfunctions as cf


ADDRESSES = (0x2017, 0x2018, 0x2019)


def read_sdo_raw(elac, address):
    """Legge il valore raw di un oggetto SDO all'indice indicato."""
    return elac.sdo[address].raw


def read_concatenated_value(elac):
    """
    Legge 0x2017, 0x2018 e 0x2019 e ritorna:
      - dizionario {indirizzo: valore_raw}
      - stringa concatenata dei valori raw
    """
    values = {}

    for address in ADDRESSES:
        values[address] = read_sdo_raw(elac, address)

    concatenated = "".join(str(values[address]) for address in ADDRESSES)
    return values, concatenated


def main():
    try:
        rpsoem = RpPysoem()
        elac = rpsoem.node

        # Diagnostica EtherCAT, come nello script Test_Ethercat.py
        ok = rpsoem.ethercat_debug()
        if not ok:
            print("\nSTOP: controllare hardware EtherCAT, EEPROM o stato del nodo prima della lettura SDO.")
            return 2
        
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.1)

        cf.reset_drive(elac)
        time.sleep(1.5)

        elac.sdo.download(0x6060, 0, (6).to_bytes(1, "little", signed=True))
        time.sleep(0.05)

        try:
            print(f"[INFO] Mode actual: {elac.sdo[0x6061].raw}")
        except Exception:
            pass
       
        values, concatenated = read_concatenated_value(elac)

        print("Lettura SDO completata:")
        for i, address in enumerate(ADDRESSES):
            print(f"UID[{i}]  = 0x{values[address]:08X}")

        #print(f"Valore concatenato: {concatenated}")
        return 0

    except KeyboardInterrupt:
        print("\n[INFO] Lettura interrotta dall'utente")
        return 130

    except Exception as e:
        print(f"[ERROR] Lettura SDO fallita: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

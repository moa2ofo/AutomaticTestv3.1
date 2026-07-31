
# -*- coding: utf-8 -*-
import sys
import os

from lib.ecat_common_func import RpPysoem
from elac_tests.ELAC_PdoMapping import run_sdo_comm_test
from elac_tests.ELAC_PrintObjectDictionary import read_object_dictionary

def main():
    if len(sys.argv) < 2:
        print("Errore: primo argomento mancante (pos|vel).")
        sys.exit(1)

    test_type = sys.argv[1].strip().lower()


    stop_file = os.getenv("STOP_FILE")
    if stop_file:
        print(f"[INFO] STOP_FILE: {stop_file}")

    rpsoem = RpPysoem()
    elac = rpsoem.node

    # Diagnostica EtherCAT
    ok = rpsoem.ethercat_debug()
    if not ok:
        print("\nSTOP: Fix EtherCAT hardware/EEPROM/state before CiA402 tests.")
        sys.exit(2)

    def finish(test_name, result):
        print(f"EtherCAT: {test_name} {'OK' if result else 'FALLITO'}")
        sys.exit(0 if result else 3)


    try:
        if test_type == "read":
            ok = read_object_dictionary(elac)
            finish("Read Object Dictionary", ok)


        elif test_type == "pdomapping":
            ok = run_sdo_comm_test(elac)
            finish("Read Object Dictionary", ok)

        else:
            print(f"Errore: comando '{test_type}' non riconosciuto.")
            sys.exit(1)

    except ValueError:
        print("Errore: i parametri devono essere numerici.")
        sys.exit(1)

if __name__ == "__main__":
    main()

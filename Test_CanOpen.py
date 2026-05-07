
# -*- coding: utf-8 -*-
import sys
import os

from lib.ecat_common_func import RpPysoem
from lib.cancommonfunctions import initCANopen

# tests
from elac_tests.ELAC_TestProfileVelocity import run_velocity_test
from elac_tests.ELAC_TestProfilePosition import run_position_test
from elac_tests.ELAC_TestHoming37 import run_homing_test
from elac_tests.ELAC_TestProfileTorque import run_torque_test

USO = (
    "Uso:\n"
    "  Test_CanOpen.py pos <target_pos_1> <target_pos_2> <max_velocity>\n"
    "  Test_CanOpen.py vel <velocita> <tempo>\n"
)

def main():
    if len(sys.argv) < 2:
        print("Errore: primo argomento mancante (pos|vel).")
        print(USO)
        sys.exit(1)

    test_type = sys.argv[1].strip().lower()

    # === opzionale: stop cooperativo ===
    stop_file = os.getenv("STOP_FILE")  # passato dalla GUI
    if stop_file:
        print(f"[INFO] STOP_FILE: {stop_file}")

    ELAC_eds = "ELAC.eds"
    network = initCANopen()
    elac = None
    for node_id in network:
        if node_id == 1:
            elac = network[node_id]
            break
    if elac is None:
        print("Errore: nodo CANopen ID=1 non trovato.")
        sys.exit(1)

    try:
        if test_type == "pos":
            if len(sys.argv) < 5:
                print("Errore: servono 3 parametri numerici per 'pos'.")
                print(USO)
                sys.exit(1)
            p1 = int(float(sys.argv[2]))  # consenti anche "12.0"
            p2 = int(float(sys.argv[3]))
            p3 = int(float(sys.argv[4]) * 10000)
            ok = run_position_test(elac, p1, p2, p3, stop_file=stop_file)
            print("CANopen: Test di posizione", "OK" if ok else "FALLITO")

        elif test_type == "vel":
            if len(sys.argv) < 4:
                print("Errore: servono 2 parametri numerici per 'vel'.")
                print(USO)
                sys.exit(1)
            p1 = int(float(sys.argv[2]) * 10000)  # velocit scalata
            p2 = int(float(sys.argv[3]))          # tempo (s)
            ok = run_velocity_test(elac, p1, p2, stop_file=stop_file)
            print("CANopen: Test di velocit", "OK" if ok else "FALLITO")

        else:
            print("Errore: tipo di test non riconosciuto. Usa 'pos' o 'vel'.")
            print(USO)
            sys.exit(1)

    except ValueError:
        print("Errore: i parametri devono essere numerici.")
        sys.exit(1)

if __name__ == "__main__":
    main()

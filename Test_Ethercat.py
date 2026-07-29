
# -*- coding: utf-8 -*-
import sys
import os

from lib.ecat_common_func import RpPysoem
from elac_tests.ELAC_TestProfileVelocity import run_velocity_test
from elac_tests.ELAC_TestProfilePosition import run_position_test
from elac_tests.ELAC_TestPosition import run_singlePosition_test
from elac_tests.ELAC_TestTrajectory import run_trajectory_test
from elac_tests.ELAC_TestHome import run_homing_test
from elac_tests.ELAC_TestBrake import run_brake_test
from elac_tests.ELAC_PrintObjectDictionary import read_object_dictionary

USO = (
    "Uso:\n"
    "  Test_Ethercat.py pos <target_pos_1> <target_pos_2> <max_velocity>\n"
    "  Test_Ethercat.py vel <velocita> <tempo>\n"
)

def main():
    if len(sys.argv) < 2:
        print("Errore: primo argomento mancante (pos|vel).")
        print(USO)
        sys.exit(1)

    test_type = sys.argv[1].strip().lower()

    # ✅ Leggi STOP_FILE dall'ambiente (passato dalla GUI)
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

    try:
        if test_type == "pos":
            if len(sys.argv) < 5:
                print("Errore: servono 3 parametri numerici per 'pos'.")
                print(USO)
                sys.exit(1)
            p1 = float(sys.argv[2])
            p2 = float(sys.argv[3])
            p3 = float(sys.argv[4]) * 10000  # scaling rpm->unità
            if p3 > 10*10000:
                    p3 = 10*10000 
            ok = run_position_test(elac, p1, p2, p3, stop_file=stop_file)  # ✅
            print("EtherCAT: Test di posizione", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        elif test_type == "singlepos":
            if len(sys.argv) < 4:
                print("Errore: servono 2 parametri numerici per 'pos'.")
                print(USO)
                sys.exit(1)

            target_angle = float(sys.argv[2])
            max_velocity = float(sys.argv[3]) * 10000  # scaling rpm -> unita drive
            max_velocity = 50 * 10000
            ok = run_singlePosition_test(elac, target_angle, max_velocity, stop_file=stop_file)
            print("EtherCAT: Test di posizione", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        elif test_type == "trajectory":
            if len(sys.argv) < 5:
                print("Errore: servono 2 parametri numerici per 'pos'.")
                print(USO)
                sys.exit(1)

            delta_angle = float(sys.argv[2])
            time_based_ms = float(sys.argv[3])
            final_angle_target = float(sys.argv[4]) 
            max_velocity = 50 * 10000
            ok = run_trajectory_test(elac, delta_angle,time_based_ms,final_angle_target, stop_file=stop_file)
            print("EtherCAT: Test di posizione", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        elif test_type == "read":
            ok = read_object_dictionary(elac)
            print("Read OD", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        elif test_type == "vel":
            if len(sys.argv) < 4:
                print("Errore: servono 2 parametri numerici per 'vel'.")
                print(USO)
                sys.exit(1)
            p1 = float(sys.argv[2]) * 10000  # velocita scalata
            #saturazione p1
            if p1 > 10*10000:
                    p1 = 10*10000 
            p2 = float(sys.argv[3])          # tempo (s)
            #saturazione p2
            if p2 > 5:
                p2 = 5
            ok = run_velocity_test(elac, p1, p2, stop_file=stop_file)       # ✅
            print("EtherCAT: Test di velocita", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        elif test_type == "home":
            # Homing secondo CiA 402

            # eventuali parametri opzionali (es. velocità di homing)
            if len(sys.argv) < 3:
                home_speed = 2000  # default (unità drive)
            else:
                home_speed = float(sys.argv[2]) * 10000  # scaling come gli altri

            # saturazione sicurezza
            if home_speed > 5 * 10000:
                home_speed = 5 * 10000

            ok = run_homing_test(elac, home_speed, stop_file=stop_file)

            print("EtherCAT: Homing CiA402", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        elif test_type == "brake":
            if len(sys.argv) < 3:
                print("Errore: uso corretto:")
                print("  Test_Ethercat.py brake <mode> [command]")
                print("Esempi:")
                print("  Test_Ethercat.py brake 1 1   # manuale, applica freno")
                print("  Test_Ethercat.py brake 1 0   # manuale, rilascia freno")
                print("  Test_Ethercat.py brake 0     # automatico")
                sys.exit(1)

            mode = int(sys.argv[2])
            command = int(sys.argv[3]) if len(sys.argv) >= 4 else None

            ok = run_brake_test(elac, mode, command)

            print("EtherCAT: Test freno", "OK" if ok else "FALLITO")
            sys.exit(0 if ok else 3)
        else:
            print("Errore: tipo di test non riconosciuto. Usa 'pos' o 'vel'.")
            print(USO)
            sys.exit(1)

    except ValueError:
        print("Errore: i parametri devono essere numerici.")
        sys.exit(1)

if __name__ == "__main__":
    main()

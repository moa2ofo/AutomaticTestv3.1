
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

    def clamp(value, maximum):
        return min(value, maximum)
    try:
        if test_type == "pos":
            if len(sys.argv) < 5:
                print("Errore: servono 3 parametri numerici per 'pos'.")
                sys.exit(1)

            target1 = float(sys.argv[2])
            target2 = float(sys.argv[3])
            max_velocity = clamp(float(sys.argv[4]) * 10000, 10 * 10000)

            ok = run_position_test(
                elac,
                target1,
                target2,
                max_velocity,
                stop_file=stop_file
            )

            finish("Test di posizione", ok)

        elif test_type == "singlepos":
            if len(sys.argv) < 4:
                print("Errore: servono 2 parametri numerici per 'singlepos'.")
                sys.exit(1)

            target_angle = float(sys.argv[2])

            # velocità fissa
            max_velocity = 50 * 10000

            ok = run_singlePosition_test(
                elac,
                target_angle,
                max_velocity,
                stop_file=stop_file
            )

            finish("Test di posizione", ok)

        elif test_type == "trajectory":
            if len(sys.argv) < 5:
                print("Errore: servono 3 parametri numerici per 'trajectory'.")
                sys.exit(1)

            delta_angle = float(sys.argv[2])
            time_based_ms = float(sys.argv[3])
            final_angle = float(sys.argv[4])

            ok = run_trajectory_test(
                elac,
                delta_angle,
                time_based_ms,
                final_angle,
                stop_file=stop_file
            )

            finish("Test traiettoria", ok)

        elif test_type == "read":
            ok = read_object_dictionary(elac)
            finish("Read Object Dictionary", ok)

        elif test_type == "vel":
            if len(sys.argv) < 4:
                print("Errore: servono 2 parametri numerici per 'vel'.")
                sys.exit(1)

            velocity = clamp(float(sys.argv[2]) * 10000, 10 * 10000)
            duration = clamp(float(sys.argv[3]), 5)

            ok = run_velocity_test(
                elac,
                velocity,
                duration,
                stop_file=stop_file
            )

            finish("Test di velocità", ok)

        elif test_type == "home":

            if len(sys.argv) >= 3:
                home_speed = clamp(float(sys.argv[2]) * 10000, 5 * 10000)
            else:
                home_speed = 2000

            ok = run_homing_test(
                elac,
                home_speed,
                stop_file=stop_file
            )

            finish("Homing CiA402", ok)

        elif test_type == "brake":
            if len(sys.argv) < 3:
                print("Errore: uso corretto:")
                print("  Test_Ethercat.py brake <mode> [command]")
                print("")
                print("Esempi:")
                print("  Test_Ethercat.py brake 0")
                print("  Test_Ethercat.py brake 1 1")
                print("  Test_Ethercat.py brake 1 0")
                sys.exit(1)

            mode = int(sys.argv[2])
            command = int(sys.argv[3]) if len(sys.argv) > 3 else None

            ok = run_brake_test(elac, mode, command)

            finish("Test freno", ok)

        else:
            print(f"Errore: comando '{test_type}' non riconosciuto.")
            sys.exit(1)

    except ValueError:
        print("Errore: i parametri devono essere numerici.")
        sys.exit(1)

if __name__ == "__main__":
    main()

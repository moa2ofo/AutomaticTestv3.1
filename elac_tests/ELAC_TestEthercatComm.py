
import sys
import os
import time
import math
import csv
from datetime import datetime

# Allow import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lib.cancommonfunctions as cf


def _should_stop(stop_file):
    """Ritorna True se è stato richiesto lo stop cooperativo."""
    if not stop_file:
        return False
    try:
        return os.path.exists(stop_file)
    except Exception:
        return False


def _cleanup_stop_file(stop_file):
    if not stop_file:
        return
    try:
        if os.path.exists(stop_file):
            os.remove(stop_file)
            print(f"[INFO] STOP_FILE rimosso (test): {stop_file}")
    except Exception as e:
        print(f"[WARN] impossibile rimuovere STOP_FILE (test): {e}")


def run_velocity_test(elac, par1, par2, stop_file=None):
    """
    Runs a velocity profile test on the elac drive.
    Returns True if the test completes (anche se interrotto) senza eccezioni non gestite.
    par1: target velocity (unità del drive, già scalata)
    par2: durata in secondi
    stop_file: path a file stop cooperativo (se esiste, interrompe il test)
    """
    rows = []
    try:
        print("\033[32mBegin Velocity test\033[0m")


        time.sleep(0.05)
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.05)
        #cf.read_faults_via_sdo(elac)
        #time.sleep(0.05)
        sw_ver = cf.read_software_version(elac)
        sw = cf.get_sw(elac)
        print(f"Statusword: 0x{sw:04X}")
        print(f"Software version: '{sw_ver}'")
        cf.reset_drive(elac)

        print("ELAC SOD ############")
        elac.sdo.download(0x6060, 0, (3).to_bytes(1, 'little'))                    # MF: modes of operation
        elac.sdo.download(0x6083, 0, (80000).to_bytes(4, 'little'))                # MF: Profile acc
        elac.sdo.download(0x6084, 0, (80000).to_bytes(4, 'little'))                # MF: Profile dec
        elac.sdo.download(0x606D, 0, (5000).to_bytes(2, 'little'))                 # MF: Vel window
        elac.sdo.download(0x606E, 0, (100).to_bytes(2, 'little'))                  # MF: Vel window time
        elac.sdo.download(0x606F, 0, (5000).to_bytes(2, 'little'))                 # MF: Vel threshold
        elac.sdo.download(0x6070, 0, (100).to_bytes(2, 'little'))                  # MF: Vel threshold time
        # elac.sdo.download(0x607F, 0, (100000).to_bytes(4, 'little'))             # Max profile velocity

        elac.sdo.download(0x60FF, 0, (0).to_bytes(4, 'little', signed=True))       # Target Velocity
        elac.sdo.download(0x6073, 0, (2000).to_bytes(2, 'little'))                 # Max Current
        elac.sdo.download(0x6075, 0, int(5000 / math.sqrt(2)).to_bytes(4, 'little'))  # Motor rated Current
        elac.sdo.download(0x6072, 0, (2000).to_bytes(2, 'little', signed=True))    # Max Torque
        elac.sdo.download(0x6076, 0, (1000).to_bytes(4, 'little', signed=True))    # Motor rated Torque

        print(f"Max Current: {elac.sdo[0x6073].raw}")
        print(f"Max Torque: {elac.sdo[0x6072].raw}")
        print(f"Motor rated Current: {elac.sdo[0x6075].raw}")
        print(f"Motor rated Torque: {elac.sdo[0x6076].raw}")

        cf.go_to_op_enabled(elac)

        sample_dt = 0.05  # seconds

        # Create output folder
        output_dir = os.path.join(os.path.dirname(__file__), "test_results")
        os.makedirs(output_dir, exist_ok=True)

        # One single file for the full test
        test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"velocity_test_{test_timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        global_sample_index = 0

        # Esegui avanti e poi indietro
        for target_vel in (int(par1), -int(par1)):
            # Se è stato richiesto lo stop prima di iniziare il ramo, esci
            if _should_stop(stop_file):
                print("[INFO] Stop richiesto prima del secondo ramo.")
                break

            # Set target velocity
            elac.sdo.download(0x60FF, 0, target_vel.to_bytes(4, 'little', signed=True))

            t0 = time.time()
            local_sample_index = 0

            while (time.time() - t0) < par2:
                if _should_stop(stop_file):
                    print("[INFO] Stop cooperativo ricevuto: esco dal ciclo.")
                    break

                elapsed = time.time() - t0

                # Live readings
                torque = elac.sdo[0x6077].raw      # Actual torque
                current = elac.sdo[0x6078].raw     # Actual current
                vel_act = elac.sdo[0x606C].raw     # Actual speed
                pos_act = elac.sdo[0x6064].raw     # Actual position

                # Live print
                print(
                    f"\rTarget:{target_vel:>7}  "
                    f"Tq:{torque:>6}  "
                    f"I:{current:>6}  "
                    f"Vel:{vel_act:>8}  "
                    f"Pos:{pos_act:>10}",
                    end="",
                    flush=True
                )

                # Save sample (FIX: aggiunto local_sample_index)
                rows.append([
                    global_sample_index,
                    local_sample_index,
                    round(elapsed, 3),
                    target_vel,
                    torque,
                    current,
                    vel_act,
                    pos_act
                ])

                global_sample_index += 1
                local_sample_index += 1
                time.sleep(sample_dt)

            print()

            # Stop motore tra i rami o se interrotto
            elac.sdo.download(0x60FF, 0, (0).to_bytes(4, 'little', signed=True))
            time.sleep(2)

            sw = elac.sdo[0x6041].raw
            print(f"Statusword: 0x{sw:04X}")
            
            # Se abbiamo interrotto dentro il while, esci dal for
            if _should_stop(stop_file):
                break

        # Salva quanto raccolto (anche se interrotto)
        with open(filepath, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "global_sample_index",
                "local_sample_index",
                "elapsed_s",
                "target_velocity",
                "actual_torque",
                "actual_current",
                "actual_speed",
                "actual_position"
            ])
            writer.writerows(rows)

        print(f"Data saved in: {filepath}")

        # Porta in stato sicuro
        cf.go_to_switch_on_disabled(elac)
        print("\033[32mVelocity test completed.\033[0m")
        return True        




    except Exception as e:
        # Best-effort: prova a fermare motore e disabilitare
        try:
            elac.sdo.download(0x60FF, 0, (0).to_bytes(4, 'little', signed=True))
            cf.go_to_switch_on_disabled(elac)
        except Exception:
            pass
        print(f"\033[31mVelocity test failed: {e}\033[0m")
        return False
    finally:
        _cleanup_stop_file(stop_file)  # ✅




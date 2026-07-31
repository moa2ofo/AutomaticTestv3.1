
import sys
import os
import time
import math


# Allow import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lib.cancommonfunctions as cf





def run_sdo_comm_test(elac):
    """
    Runs a velocity profile test on the elac drive.
    Returns True if the test completes (anche se interrotto) senza eccezioni non gestite.
    par1: target velocity (unità del drive, già scalata)
    par2: durata in secondi
    stop_file: path a file stop cooperativo (se esiste, interrompe il test)
    """

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

    except Exception as e:
        # Best-effort: prova a fermare motore e disabilitare
        try:
            elac.sdo.download(0x60FF, 0, (0).to_bytes(4, 'little', signed=True))
            cf.go_to_switch_on_disabled(elac)
        except Exception:
            pass
        print(f"\033[31mVelocity test failed: {e}\033[0m")
        return False





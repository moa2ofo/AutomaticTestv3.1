
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


    print(f"Mode of operation: {elac.sdo[0x6060].raw}")



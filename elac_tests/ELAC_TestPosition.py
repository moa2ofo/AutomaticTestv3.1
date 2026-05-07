import sys
import os
import time

# Allow import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lib.cancommonfunctions as cf


def _should_stop(stop_file):
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


def _wait_until_target_reached_with_stop(elac, stop_file, poll_s=0.05, timeout_s=10.0):
    """
    Attende il 'target reached' in modo cooperativo.
    Ritorna True se target raggiunto, False se interrotto o timeout.
    """
    start = time.time()
    while True:
        if _should_stop(stop_file):
            return False
        '''
        try:
            # Implementazione robusta: controlla lo statusword 0x6041 bit 10 (target reached)
            print(f"Target position reached. Actual position: {elac.sdo[0x6064].raw}")
            # Statusword 0x6041, bit 10 = target reached
            sw = elac.sdo[0x6041].raw
            target_reached = bool(sw & (1 << 10))
        except Exception:
            target_reached = False

        if target_reached:
            return True

        if timeout_s is not None and (time.time() - start) > timeout_s:
            return False
        '''
        time.sleep(poll_s)


def run_singlePosition_test(elac, target_position, max_velocity, stop_file=None):
    """
    DS402 Profile Position Mode:
    riceve una sola posizione target in unita' drive
    e porta l'attuatore a quella posizione.
    """
    TARGET_POS = int(target_position)
    MAX_VELOCITY = 200000

    ACCEL = 140000
    DECEL = 140000

    print("\033[32mBegin Single Target Position Test (CiA 402 / DS402)\033[0m")
    print(f"Target position [units]: {TARGET_POS}")

    try:
        # 1) Init/reset
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.05)
        cf.reset_drive(elac)
        time.sleep(1.5)

        # 2) Config
        elac.sdo[0x6092][1].raw = 6000
        time.sleep(0.01)
        elac.sdo[0x6091][1].raw = 1
        time.sleep(0.01)
        elac.sdo[0x6091][2].raw = 1
        time.sleep(0.01)

        # Polarity: inversione del verso
        # 0x607E = Polarity
        # imposto -1 per far girare al contrario
        elac.sdo.download(0x607E, 0, (-1).to_bytes(1, "little", signed=True))
        time.sleep(0.01)
        
        elac.sdo[0x607F].raw = max(300000, MAX_VELOCITY)
        time.sleep(0.01)
        
        elac.sdo.download(0x6081, 0, MAX_VELOCITY.to_bytes(4, "little", signed=False))
        time.sleep(0.01)
        elac.sdo.download(0x6083, 0, ACCEL.to_bytes(4, "little", signed=False))
        time.sleep(0.01)
        elac.sdo.download(0x6084, 0, DECEL.to_bytes(4, "little", signed=False))
        time.sleep(0.01)
        
        # Profile Position Mode
        elac.sdo.download(0x6060, 0, (1).to_bytes(1, "little", signed=True))
        time.sleep(0.01)

        cf.go_to_op_enabled(elac)
        time.sleep(0.1)

        if _should_stop(stop_file):
            print("[INFO] Stop cooperativo: uscita prima di impostare il target.")
            return False

        # opzionale: azzera il bit new set-point prima del comando
        elac.sdo.download(0x6040, 0, (0x000F).to_bytes(2, "little", signed=False))
        time.sleep(0.01)

        # scrive il target
        elac.sdo[0x607A].raw = int((TARGET_POS * 6000 * 100) / 360)
        print(f"Set target position to: {TARGET_POS}")

        # nuovo set-point
        elac.sdo.download(0x6040, 0, (0x001F).to_bytes(2, "little", signed=False))
        time.sleep(0.01)

        # alcuni drive richiedono di togliere di nuovo il bit 4 dopo il fronte
        elac.sdo.download(0x6040, 0, (0x000F).to_bytes(2, "little", signed=False))

        ok = _wait_until_target_reached_with_stop(elac, stop_file, poll_s=0.05, timeout_s=100.0)
        if not ok:
            print("[INFO] Movimento interrotto, timeout o target non raggiunto.")
            return False

        print(f"Target position reached. Actual position: {elac.sdo[0x6064].raw}")

        cf.go_to_switch_on_disabled(elac)
        print("\033[32mSingle target position test completed.\033[0m")
        return True

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    except Exception as e:
        print(f"\033[31mPosition test failed: {e}\033[0m")
    finally:
        try:
            cf.go_to_switch_on_disabled(elac)
        except Exception:
            pass
        _cleanup_stop_file(stop_file)

    return False
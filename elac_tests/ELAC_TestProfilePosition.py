
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


def _wait_until_target_reached_with_stop(elac, stop_file, poll_s=0.05, timeout_s=None):
    """
    Attende il 'target reached' in modo cooperativo.
    Ritorna True se target raggiunto, False se interrotto o timeout.
    """
    start = time.time()
    while True:
        if _should_stop(stop_file):
            return False
        # Se hai una funzione non bloccante per controllare il flag, usala qui:
        # Esempio: cf.IsTargetReached(elac) -> bool
        try:
            # Implementazione robusta: controlla lo statusword 0x6041 bit 10 (target reached)
            print(f"Target position reached. Actual position: {elac.sdo[0x6064].raw}")
            sw = elac.sdo[0x6041].raw
            target_reached = bool(sw & (1 << 10))
        except Exception:
            # Fallback: se hai una helper non bloccante
            target_reached = False

        if target_reached:
            return True

        if timeout_s is not None and (time.time() - start) > timeout_s:
            return False

        time.sleep(poll_s)

def run_position_test(elac, par1, par2, par3, stop_file=None):
    """
    Profile Position Mode test con stop cooperativo.
    Muove tra due posizioni (P1 e P2) due volte.
    Ritorna True se completa senza eccezioni non gestite (anche se interrotto).
    """
    TARGET_POS_1 = int(par1)
    TARGET_POS_2 = int(par2)
    MAX_VELOCITY = int(par3)
    ACCEL = 140000
    DECEL = 140000

    print("\033[32mBegin Profile Position Mode Test (CiA 402)\033[0m")

    try:
        # 1) Init/reset
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.05)
        cf.reset_drive(elac)
        time.sleep(1.5)

        # 2) Config
        elac.sdo[0x6092][1].raw = 6000      # feed constant - feed
        time.sleep(0.01)
        elac.sdo[0x6091][1].raw = 1         # gear ratio - motor rev
        time.sleep(0.01)
        elac.sdo[0x6091][2].raw = 1         # gear ratio - shaft rev
        time.sleep(0.01)
        elac.sdo[0x607F].raw = max(300000, MAX_VELOCITY)  # >= MAX_VELOCITY
        time.sleep(0.01)

        elac.sdo.download(0x6081, 0, MAX_VELOCITY.to_bytes(4, 'little'))  # Profile Velocity
        time.sleep(0.01)
        elac.sdo.download(0x6083, 0, ACCEL.to_bytes(4, 'little'))         # Acc
        time.sleep(0.01)
        elac.sdo.download(0x6084, 0, DECEL.to_bytes(4, 'little'))         # Dec
        time.sleep(0.01)

        elac.sdo.download(0x6060, 0, (1).to_bytes(1, 'little'))           # Mode = Profile Position
        cf.go_to_op_enabled(elac)

        # 3) Sequenza di due movimenti (P1 -> P2 -> P1)
        sequence = [TARGET_POS_1, TARGET_POS_2, TARGET_POS_1]

        for idx in range(1, len(sequence)):
            if _should_stop(stop_file):
                print("[INFO] Stop cooperativo: uscita prima di impostare il target.")
                break

            current_target = sequence[idx]
            elac.sdo[0x607A].raw = current_target
            print(f"Set target position to: {current_target}")

            # Trigger movimento
            elac.sdo.download(0x6040, 0, (0x0F).to_bytes(2, 'little'))  # reset New Set-point
            time.sleep(0.01)
            elac.sdo.download(0x6040, 0, (0x1F).to_bytes(2, 'little'))  # set New Set-point

            # Attesa cooperativa del target reached
            ok = _wait_until_target_reached_with_stop(elac, stop_file, poll_s=0.05, timeout_s=None)
            
            if not ok:
                print("[INFO] Movimento interrotto o non concluso: esco.")
                break

            print(f"Target position reached. Actual position: {elac.sdo[0x6064].raw}")
            time.sleep(0.5)

        # 4) Safe state
        cf.go_to_switch_on_disabled(elac)
        print("\033[32mPosition test completed.\033[0m")
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
        _cleanup_stop_file(stop_file)  # ✅
    return False


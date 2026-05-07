import sys
import os
import time
import struct

# Allow import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lib.cancommonfunctions as cf


# =========================
# STOP MANAGEMENT
# =========================

def _should_stop(stop_file):
    return stop_file and os.path.exists(stop_file)


def _cleanup_stop_file(stop_file):
    if stop_file and os.path.exists(stop_file):
        try:
            os.remove(stop_file)
            print(f"[INFO] STOP_FILE rimosso: {stop_file}")
        except Exception as e:
            print(f"[WARN] impossibile rimuovere STOP_FILE: {e}")


# =========================
# ENCODER CONVERSION
# =========================

def _decode_encoder_value(raw):
    """
    Decodifica valore encoder (assunto IEEE754 float32 da uint32)
    """
    try:
        as_bytes = int(raw).to_bytes(4, byteorder='big', signed=False)
        value_float = struct.unpack('>f', as_bytes)[0]
        return int(value_float * 100)
    except Exception:
        return None


# =========================
# HOMING TEST (CiA 402 - Method 37)
# =========================

def run_homing_test(elac, home_speed=20000, home_offset=None, stop_file=None):

    HOMING_SPEED = int(home_speed)

    print("\033[32mBegin Homing Test (CiA 402 / Method 37)\033[0m")
    print(f"Homing speed: {HOMING_SPEED}")

    try:

        # =========================
        # 1) RESET DRIVE
        # =========================
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.1)

        cf.reset_drive(elac)
        time.sleep(1.5)

        if _should_stop(stop_file):
            print("[INFO] Stop prima della configurazione")
            return False

        # =========================
        # 2) MODE = HOMING
        # =========================
        elac.sdo.download(0x6060, 0, (6).to_bytes(1, "little", signed=True))
        time.sleep(0.05)

        try:
            print(f"[INFO] Mode actual: {elac.sdo[0x6061].raw}")
        except Exception:
            pass

        # =========================
        # 3) HOMING METHOD = 37
        # =========================
        elac.sdo.download(0x6098, 0, (37).to_bytes(1, "little", signed=True))
        print("[INFO] Homing Method 37 impostato")
        time.sleep(0.05)

        # =========================
        # 4) AUTO HOME OFFSET (optional encoder-based)
        # =========================
        if home_offset is None:
            try:
                encoder_raw = elac.sdo[0x201F].raw
                result = _decode_encoder_value(encoder_raw)

                if result is not None:
                    home_offset = -(int(result * 6000 / 360))
                    print(f"[INFO] Auto Home Offset calcolato: {home_offset}")
            except Exception as e:
                print(f"[WARN] Encoder read failed: {e}")
                home_offset = 0

        # =========================
        # 5) SET HOME OFFSET
        # =========================
        try:
            elac.sdo.download(
                0x607C,
                0,
                int(home_offset).to_bytes(4, "little", signed=True)
            )
            print(f"[INFO] 0x607C Home Offset: {home_offset}")
        except Exception as e:
            print(f"[WARN] 0x607C non scritto: {e}")

        # =========================
        # 6) HOMING SPEED PARAMS
        # =========================
        try:
            elac.sdo[0x6099][1].raw = HOMING_SPEED
            elac.sdo[0x6099][2].raw = HOMING_SPEED
        except Exception:
            pass

        # =========================
        # 7) ENABLE OPERATION
        # =========================
        cf.go_to_op_enabled(elac)
        time.sleep(0.2)

        if _should_stop(stop_file):
            print("[INFO] Stop prima start homing")
            return False

        # =========================
        # 8) START HOMING (0 -> 1 bit4)
        # =========================
        elac.sdo.download(0x6040, 0, (0x000F).to_bytes(2, "little", signed=False))
        time.sleep(0.05)

        elac.sdo.download(0x6040, 0, (0x001F).to_bytes(2, "little", signed=False))
        print("[INFO] Homing start triggered")

        # =========================
        # 9) WAIT COMPLETION
        # =========================
        start = time.time()
        timeout_s = 10.0

        while True:

            if _should_stop(stop_file):
                print("[INFO] Homing interrotto da STOP")
                return False

            try:
                status = elac.sdo[0x6041].raw

                homing_attained = bool(status & (1 << 12))

                print(f"[INFO] SW=0x{status:04X} attained={homing_attained}")

                if homing_attained:
                    break

            except Exception:
                pass

            if time.time() - start > timeout_s:
                print("[ERROR] Timeout homing")
                return False

            time.sleep(0.05)

        # =========================
        # 10) RESULT
        # =========================
        actual = elac.sdo[0x6064].raw

        print("\033[32mHoming completed successfully\033[0m")
        print(f"Actual position: {actual}")

        cf.go_to_switch_on_disabled(elac)

        return True

    except KeyboardInterrupt:
        print("\n[INFO] Interrotto da utente")

    except Exception as e:
        print(f"\033[31mHoming failed: {e}\033[0m")

    finally:
        try:
            cf.go_to_switch_on_disabled(elac)
        except Exception:
            pass

        _cleanup_stop_file(stop_file)

    return False
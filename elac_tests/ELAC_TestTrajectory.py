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

def run_trajectory_test(elac, delta_angle, time_base_ms, final_angle_target, stop_file=None):
    """
    Time-based trajectory:
    - Hold 0° until actual position is ~0 (±1°)
    - Then send N * delta_angle every time_base_ms
    - Stop when actual position > 270°
    """

    TIME_BASE_S = time_base_ms / 1000.0
    DELTA_INC = float(delta_angle)

    def deg_to_units(deg):
        return int((deg * 6000 * 100) / 360)

    def units_to_deg(units):
        return (units * 360.0) / (6000 * 100)

    print("\033[32mBegin Trajectory Test (time-based)\033[0m")

    try:
        # --- INIT ---
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.05)
        cf.reset_drive(elac)
        time.sleep(1.5)

        # Config
        elac.sdo[0x6092][1].raw = 6000
        time.sleep(0.01)
        elac.sdo[0x6091][1].raw = 1
        time.sleep(0.01)
        elac.sdo[0x6091][2].raw = 1
        time.sleep(0.01)

        # Polarity
        elac.sdo.download(0x607E, 0, (-1).to_bytes(1, "little", signed=True))
        time.sleep(0.01)

        # Profile Position Mode
        elac.sdo.download(0x6060, 0, (1).to_bytes(1, "little", signed=True))
        time.sleep(0.01)

        cf.go_to_op_enabled(elac)
        time.sleep(0.1)

        # Reset controlword
        elac.sdo.download(0x6040, 0, (0x000F).to_bytes(2, "little"))

        # --- STEP 1: GO TO 0° AND WAIT ---
        print("[INFO] Moving to 0°...")

        elac.sdo[0x607A].raw = deg_to_units(0)

        elac.sdo.download(0x6040, 0, (0x001F).to_bytes(2, "little"))
        time.sleep(0.01)
        elac.sdo.download(0x6040, 0, (0x000F).to_bytes(2, "little"))

        # Wait until position ~0 ±1°
        while True:
            if _should_stop(stop_file):
                return False

            actual_units = elac.sdo[0x6064].raw
            actual_deg = units_to_deg(actual_units)

            if abs(actual_deg) <= 1.0:
                print(f"[INFO] Reached 0° (actual: {actual_deg:.2f})")
                break

            time.sleep(0.05)

        # --- STEP 2: TRAJECTORY LOOP ---
        print("[INFO] Starting trajectory...")

        N = 1

        while True:
            if _should_stop(stop_file):
                return False

            # Read actual position
            actual_units = elac.sdo[0x6064].raw
            actual_deg = units_to_deg(actual_units)

            # Stop condition
            if actual_deg > final_angle_target:
                print(f"[INFO] Stop condition reached: {actual_deg:.2f}°")
                break
            
            # Compute next target
            DELTA_INC = float(delta_angle*(1+(actual_deg//180)))
            target_deg = N * DELTA_INC
            target_units = deg_to_units(target_deg)
            previus_target = target_deg - delta_angle;

            print(f"Target: {previus_target}° Current angle: {actual_deg:.2f}°")

            # Send target
            elac.sdo[0x607A].raw = target_units

            elac.sdo.download(0x6040, 0, (0x001F).to_bytes(2, "little"))
            time.sleep(0.001)
            elac.sdo.download(0x6040, 0, (0x000F).to_bytes(2, "little"))

            N += 1

            # Wait TIME_BASE (precise scheduling)
            #next_time += TIME_BASE_S
            #sleep_time = next_time - time.time()
            #if sleep_time > 0:
            time.sleep(TIME_BASE_S)

        print("\033[32mTrajectory test completed.\033[0m")
        return True

    except Exception as e:
        print(f"\033[31mTrajectory test failed: {e}\033[0m")
        return False

    finally:
        try:
            cf.go_to_switch_on_disabled(elac)
        except Exception:
            pass
        _cleanup_stop_file(stop_file)
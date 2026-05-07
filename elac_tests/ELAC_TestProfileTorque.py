import sys
import os
import time
import math

# Allow import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lib.cancommonfunctions as cf

def run_torque_test(elac):
    """
    Runs a profile torque mode test on the elac drive.
    
    Profile Torque Mode (CiA 402 Mode 4) allows controlling the motor by 
    commanding torque (force/current) rather than position or velocity.
    
    This test:
    1. Configures the drive for torque mode
    2. Sets torque limits and slope (rate of torque change)
    3. Commands a custom torque value and monitors the response
    4. After a short delay, Returns to zero torque and disables (for safety)
    
    Args:
        elac: The EtherCATNode object representing the drive.
    
    Returns:
        True if test completes successfully, False otherwise.
    """
    
    # Torque values in per-thousand of rated torque
    # For example: 500 = 50% of rated torque
    TORQUE_SLOPE = 150      # Rate of torque change (units per second)
    MAX_TORQUE = 1000        # Maximum torque limit (100% of rated)
    APPLIED_TORQUE = 300
    
    print("\033[32mBegin Profile Torque Mode Test (CiA 402)\033[0m")
    
    try:
        # 1. Initialization and Drive Reset
        print("Cleaning up fault conditions and resetting drive...")
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.05)
        cf.reset_drive(elac)
        time.sleep(4)
        
        # 2. Configure Torque Mode Parameters        
        # Set Mode of Operation to Profile Torque Mode (Value = 4)
        elac.sdo.download(0x6060, 0, (4).to_bytes(1, 'little'))
        
        # Configure torque parameters
        elac.sdo[0x6087].raw = TORQUE_SLOPE      # Torque slope (0x6087)
        elac.sdo[0x6072].raw = MAX_TORQUE        # Max torque (0x6072)
        elac.sdo[0x6071].raw = 0                 # Initial target torque = 0
        
        # Optional: Configure current limits for safety
        elac.sdo.download(0x6073, 0, (2000).to_bytes(2, 'little'))  # Max Current
        elac.sdo.download(0x6075, 0, int(2000/math.sqrt(2)).to_bytes(4, 'little'))  # Motor rated current
        
        # 3. Transition to Operation Enabled State
        cf.go_to_op_enabled(elac)
        
        # 4. Execute Torque Profile Test         
        elac.sdo[0x6071].raw = APPLIED_TORQUE
        
        ramp_time = APPLIED_TORQUE / TORQUE_SLOPE  # s (attenzione alle unità)
        wait_time = ramp_time + 3
        
        print(f"Waiting {wait_time:.2f}s for torque to settle")
        
        sample_dt = 0.1
        t0 = time.time()
        while time.time() - t0 < wait_time:
            torque = elac.sdo[0x6077].raw
            current = elac.sdo[0x6078].raw
            vel_act = elac.sdo[0x606C].raw
            SW = elac.sdo[0x6041].raw
            CW = elac.sdo[0x6040].raw
        
            print(f"\rTorque: {torque:>6}  Current: {current:>6}  Vel: {vel_act:>8} SW: {SW:>6} CW: {CW:>6}", end="", flush=True)
            time.sleep(sample_dt)
        
        print()  # va a capo
        
        # 5. Safety: Return to zero torque
        elac.sdo[0x6071].raw = 0
        print(f"Waiting {wait_time:.2f}s for torque to reach zero...")
        time.sleep(wait_time)

        # 5. Safety: Return to zero torque 
        elac.sdo[0x6071].raw = 0    
        print(f"Waiting {wait_time:.2f}s for torque to reach zero...")
        time.sleep(wait_time)
        
        print("\033[32mTorque test completed successfully.\033[0m")
        return True
        
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        try:
            elac.sdo[0x6071].raw = 0
            time.sleep(0.5)
        except:
            pass
        return False
        
    except Exception as e:
        print(f"\033[31mTorque test failed: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 6. Cleanup
        print("Cleaning up...")
        cf.go_to_switch_on_disabled(elac)
        time.sleep(0.1)
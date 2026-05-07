import sys
import os
import time
import math

# Allow import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lib.cancommonfunctions as cf

def run_homing_test(elac, home_offset: int = 0):
    """
    Performs Homing Mode 37 (CiA 402 standard, Home to Negative limit switch,
    then positive zero search) on the ELAC drive.
    
    Args:
        elac: The EtherCATNode object representing the drive.
        home_offset: The offset (in drive units) to be applied after homing.
    """
    HOMING_METHOD = 37 # Standard method: Search positive, start negative limit switch
    
    print("\033[32mBegin Homing Mode 37 Test (CiA 402)\033[0m")
    
    try:
        # 1. Initialization and Drive Reset
        print("Cleaning up fault conditions and resetting drive...")
        cf.QuitFromFaultCondition(elac)
        time.sleep(0.05)
        cf.reset_drive(elac)
        time.sleep(1)
        
        # 2. Configure Homing Parameters
        print(f"Configuring drive for Homing Mode {HOMING_METHOD}...")
        
        # Set Mode of Operation to Homing Mode (Value = 6)
        elac.sdo.download(0x6060,0,b'\x06')
        elac.sdo.download(0x6040, 0, b'\x06\x00')
        time.sleep(0.01)
        print("Mode of Operation set to Homing (DS402 value 6)")
        
        # Set Homing Method (0x6098)
        elac.sdo.download(0x6098, 0, HOMING_METHOD.to_bytes(1, 'little'))
    
        # Set Home Offset (0x607C)
        elac.sdo.download(0x607C, 0, home_offset.to_bytes(4,'little'))
        print(f"Homing Offset (0x607C) set to: {home_offset}")
        
        # 3. Transition to Operation Enabled State
        cf.go_to_op_enabled(elac)
        print("Drive is now in Operation Enabled State.")

        # Read current position before homing
        position_before = elac.sdo[0x6064].raw
        print(f"Position before homing (0x6064): {position_before}")

        # 4. Execute Homing Sequence
        print("Starting homing procedure...")
                
        elac.sdo.download(0x6040, 0, (6).to_bytes(2, 'little'))
        time.sleep(0.01)
        elac.sdo.download(0x6040, 0, (7).to_bytes(2, 'little'))
        time.sleep(0.01)
        # Write 0x0F: Reset Controlword (Ensures Bit 8 is 0)
        elac.sdo.download(0x6040, 0, (0x0F).to_bytes(2, 'little'))
        time.sleep(0.01)

        # Write 0x10F: Set Bit 8 (Homing Operation Start) AND Enable Operation (0x0F)
        HOMING_START_CW = 0x1F
        elac.sdo.download(0x6040, 0, (HOMING_START_CW).to_bytes(2, 'little')) 
        print(f"Sent Homing Start Controlword: 0x{HOMING_START_CW:02X}")

        # Reset Homing Start bit (back to 0x0F)
        elac.sdo.download(0x6040, 0, (0x0F).to_bytes(2, 'little'))
        
        # 5. Verification
        position_after = elac.sdo[0x6064].raw
        print(f"Position after homing (0x6064): {position_after}")
        
    except Exception as e:
        print(f"\033[31mHoming test failed: {e}\033[0m")
    finally:
        # 6. Cleanup (return to Switched On Disabled state)
        cf.go_to_switch_on_disabled(elac)
        print("\033[32mHoming test completed.\033[0m")
        time.sleep(0.1)
import canopen
import time
import os
import traceback


def find_eds():
	path = f"{os.path.abspath(os.path.curdir)}\.."
	# print("we ", path)
	for root, dirs, files in os.walk(path):
		for name in files:
			if name == "ELAC.eds":
				print("eds found")
				return os.path.abspath(os.path.join(root, name))
	else:
		raise Exception('eds not found')

def initCANopen(BaudRate = 1e6):    #Default Parameter.
# M: Initialize CANopen.                                                    :M #

	nw = canopen.Network()   #NetWork.
	while True:
		try:
			nw.connect(bustype= 'socketcan',channel= 'can1',bitrate= int(BaudRate),can_filters=None)
		except:
			pass
		else:
			print('socketcan found!')
			break
		try:
			nw.connect(bustype= 'slcan',channel= 'COM10',bitrate= int(BaudRate),can_filters=None)
		except:
			pass
		else:
			print('slcan found!')
			break
		try:
			nw.connect(bustype= 'ixxat',channel= 0,bitrate= int(BaudRate),can_filters=None)
		except:
			pass
		else:
			print('ixxat found!')
			break
		try:
			nw.connect(bustype= 'pcan',channel= 'PCAN_USBBUS1',bitrate= int(BaudRate),can_filters=None)
		except:
			pass
		else:
			print('pcan found!')
			break
		try:
			nw.connect(bustype= 'vector',channel= 0,bitrate= int(BaudRate),can_filters=None,app_name='CANoe')
		except:
			pass
		else:
			print('vector found!')
			break
		raise Exception('No USB to CAN interface found!')
	repeat= True
	while(len(nw.scanner.nodes) == 0):
			nw.scanner.search()
			time.sleep(0.05)     #50ms
	for node_id in nw.scanner.nodes:
			node = nw.add_node(node_id, find_eds())
			print("Node_id is: ", node_id)
	return nw

def WaitUntilTargetReached(node):
	while True:
		StatusWordBytes = node.sdo.upload(0x6041, 0)
		StatusWordInt = int.from_bytes(StatusWordBytes, byteorder='little')
		if StatusWordInt&0x400:
			# print("StatusWord raw:", StatusWordBytes, "---> Target Reached")
			print("StatusWord int:", StatusWordInt, "---> Target Reached")
			time.sleep(0.1)
			break
		else:
			time.sleep(0.1)

def IsTargetReached(node):
	if node.sdo[0x6041].raw & 0x400:
		return 1
	else:
		return 0

def WaitUntilHomingDone(node):
	while True:
		time.sleep(0.1)
		StatusWordBytes = node.sdo.upload(0x6041, 0)
		StatusWordInt = int.from_bytes(StatusWordBytes, 'little')
		if StatusWordInt&0x2000:
			print("Homing Error!")
			while True:
				time.sleep(1)
		elif  (StatusWordInt&0x1400)==0x1400:
			print("Homed Correctly!")
			break

def PrintDictionary(node):
	print("\nNode", node, "dictionary:")
	for obj in node.object_dictionary.values():
		print(hex(obj.index), obj.name)
	print("")

def ReadErrorsUntilFirstZero(node, max_error_number=100):
	errorcounter=1
	errorlist=[]
	while True:
		lastgoterror=node.sdo[0x1003][errorcounter].raw
		errorcounter+=1
		if lastgoterror == 0 or errorcounter >= max_error_number:
			break
		errorlist.append(lastgoterror)
	return errorlist

def Calls60Node1 (network):
	for node_id in network:
			if node_id==1:
				s60=network[node_id]
				return s60
	return None

def return_Node (network, node_number):
	for node_id in network:
		if node_id == node_number:
			return network[node_id]
	return None

def Calls60Node2 (network):
	for node_id in network:
			if node_id==2:
				s60=network[node_id]
				return s60
	return None

def ReturnNodesList (network):
	node_list = []
	for node_id in network:
		node_list.append(network[node_id])
	return node_list

import time

def read_faults_via_sdo(node, max_error_history=20, retries=3, delay_s=0.05):
    """
    Read drive faults/diagnostics via SDO using the same access style
    already used in the EtherCAT test code (.raw).

    Returns a dictionary with:
      - statusword
      - in_fault
      - error_code_603F
      - error_register_1001
      - predefined_error_field_1003
      - global_errors_200A_01
      - canopen_cmd_error_200A_08
      - status_register_200A_0B
      - error_field_time_2028
    """

    def _read_raw(idx, sub=0):
        last_exc = None
        for _ in range(retries):
            try:
                if sub == 0:
                    return node.sdo[idx].raw
                return node.sdo[idx][sub].raw
            except Exception as e:
                last_exc = e
                time.sleep(delay_s)
        raise last_exc

    diag = {
        "statusword": None,
        "in_fault": None,
        "error_code_603F": None,
        "error_register_1001": None,
        "predefined_error_field_1003": [],
        "global_errors_200A_01": None,
        "canopen_cmd_error_200A_08": None,
        "status_register_200A_0B": None,
        "error_field_time_2028": []
    }

    try:
        sw = int(_read_raw(0x6041, 0))
        diag["statusword"] = sw
        diag["in_fault"] = bool(sw & 0x0008)
    except Exception as e:
        print(f"[WARN] Cannot read 0x6041:00 Statusword: {repr(e)}")

    try:
        diag["error_code_603F"] = int(_read_raw(0x603F, 0))
    except Exception as e:
        print(f"[WARN] Cannot read 0x603F:00 Error Code: {repr(e)}")

    try:
        diag["error_register_1001"] = int(_read_raw(0x1001, 0))
    except Exception as e:
        print(f"[WARN] Cannot read 0x1001:00 Error Register: {repr(e)}")

    try:
        nerr = int(_read_raw(0x1003, 0))
        nerr = min(nerr, max_error_history)
        for sub in range(1, nerr + 1):
            try:
                err = int(_read_raw(0x1003, sub))
                if err == 0:
                    break
                diag["predefined_error_field_1003"].append(err)
            except Exception as e:
                print(f"[WARN] Cannot read 0x1003:{sub:02d}: {repr(e)}")
                break
    except Exception as e:
        print(f"[WARN] Cannot read 0x1003:00 number of entries: {repr(e)}")

    try:
        diag["global_errors_200A_01"] = int(_read_raw(0x200A, 0x01))
    except Exception as e:
        print(f"[WARN] Cannot read 0x200A:01 Global Errors: {repr(e)}")

    try:
        diag["canopen_cmd_error_200A_08"] = int(_read_raw(0x200A, 0x08))
    except Exception as e:
        print(f"[WARN] Cannot read 0x200A:08 Error States Can Open Commands: {repr(e)}")

    try:
        diag["status_register_200A_0B"] = int(_read_raw(0x200A, 0x0B))
    except Exception as e:
        print(f"[WARN] Cannot read 0x200A:0B Status Register: {repr(e)}")

    try:
        ntime = int(_read_raw(0x2028, 0))
        ntime = min(ntime, max_error_history)
        for sub in range(1, ntime + 1):
            try:
                val = int(_read_raw(0x2028, sub))
                if val == 0:
                    break
                diag["error_field_time_2028"].append(val)
            except Exception as e:
                print(f"[WARN] Cannot read 0x2028:{sub:02d}: {repr(e)}")
                break
    except Exception as e:
        print(f"[WARN] Cannot read 0x2028:00 number of entries: {repr(e)}")

    print("\n========== DRIVE FAULTS VIA SDO ==========")

    if diag["statusword"] is not None:
        print(f"Statusword (0x6041):          0x{diag['statusword']:04X}")
        print(f"In fault:                     {diag['in_fault']}")

    if diag["error_code_603F"] is not None:
        print(f"Error Code (0x603F):          0x{diag['error_code_603F']:04X}")

    if diag["error_register_1001"] is not None:
        print(f"Error Register (0x1001):      0x{diag['error_register_1001']:02X}")

    if diag["global_errors_200A_01"] is not None:
        print(f"Global Errors (0x200A:01):    0x{diag['global_errors_200A_01']:08X}")

    if diag["canopen_cmd_error_200A_08"] is not None:
        print(f"CANopen Cmd Err (0x200A:08):  0x{diag['canopen_cmd_error_200A_08']:08X}")

    if diag["status_register_200A_0B"] is not None:
        print(f"Status Register (0x200A:0B):  0x{diag['status_register_200A_0B']:08X}")

    if diag["predefined_error_field_1003"]:
        print("Predefined Error Field (0x1003):")
        for i, err in enumerate(diag["predefined_error_field_1003"], start=1):
            print(f"  [{i}] 0x{err:08X}")
    else:
        print("Predefined Error Field (0x1003): empty")

    if diag["error_field_time_2028"]:
        print("Error Field Time (0x2028):")
        for i, val in enumerate(diag["error_field_time_2028"], start=1):
            print(f"  [{i}] 0x{val:08X}")
    else:
        print("Error Field Time (0x2028): empty")

    print("=========================================\n")
    return diag

import time
import pysoem

def check_ethercat_ready(master):
    master.read_state()

    print(f"Slaves found: {len(master.slaves)}")
    print(f"Expected WKC: {master.expected_wkc}")

    if not master.slaves:
        raise RuntimeError("No EtherCAT slaves available")

    for index, slave in enumerate(master.slaves):
        al_description = pysoem.al_status_code_to_string(slave.al_status)

        print(
            f"Slave {index}: "
            f"name='{slave.name}', "
            f"state=0x{slave.state:02X}, "
            f"AL status=0x{slave.al_status:04X}, "
            f"AL description='{al_description}'"
        )

        if slave.state == pysoem.INIT_STATE:
            raise RuntimeError(
                f"Slave {index} is still in INIT; "
                "CoE mailbox access is not ready"
            )

def QuitFromFaultCondition(node, deadline_s=1.0, retry_delay_s=0.05):
    """
    Cancella la condizione di fault di un nodo CiA 402.

    La funzione:
    - legge lo Statusword 0x6041;
    - verifica il bit Fault, bit 3;
    - genera un impulso sul bit Fault Reset del Controlword 0x6040, bit 7;
    - attende che il fault venga cancellato;
    - interrompe l'operazione allo scadere della deadline.

    Args:
        node: oggetto nodo che espone node.sdo[index].raw.
        deadline_s: tempo massimo, in secondi, per cancellare il fault.
        retry_delay_s: pausa tra i tentativi SDO.

    Returns:
        bool:
            True se il nodo non è in fault o il fault è stato cancellato.
            False se la deadline viene superata o si verifica un errore
            di comunicazione.
    """

    STATUSWORD_INDEX = 0x6041
    CONTROLWORD_INDEX = 0x6040

    STATUSWORD_FAULT_MASK = 0x0008
    CONTROLWORD_FAULT_RESET_MASK = 0x0080

    node_id = getattr(node, "id", "?")
    start_time = time.perf_counter()
    fault_reported = False

    while time.perf_counter() - start_time <= deadline_s:
        try:
            # Lettura dello Statusword 0x6041:00.
            statusword = node.sdo[STATUSWORD_INDEX].raw

            # Bit 3 dello Statusword: Fault.
            if (statusword & STATUSWORD_FAULT_MASK) == 0:
                if fault_reported:
                    print(f"Node {node_id} faults erased.")
                else:
                    print(f"Node {node_id} is not in fault.")

                return True

            if not fault_reported:
                print(
                    f"Node {node_id} is in fault. "
                    f"Statusword: 0x{statusword:04X}"
                )
                fault_reported = True

            # Conserva gli altri bit del Controlword.
            controlword = node.sdo[CONTROLWORD_INDEX].raw

            # Fronte di salita sul bit Fault Reset.
            node.sdo[CONTROLWORD_INDEX].raw = (
                controlword | CONTROLWORD_FAULT_RESET_MASK
            )

            time.sleep(retry_delay_s)

            # Riporta a zero solamente il bit Fault Reset.
            node.sdo[CONTROLWORD_INDEX].raw = (
                controlword & ~CONTROLWORD_FAULT_RESET_MASK
            )

            time.sleep(retry_delay_s)

        except pysoem.WkcError as exc:
            print(
                f"EtherCAT WKC error while resetting node {node_id}: {exc}"
            )
            return False

        except pysoem.SdoError as exc:
            print(
                f"SDO error while accessing 0x6040/0x6041 "
                f"on node {node_id}: {exc}"
            )
            return False

        except pysoem.MailboxError as exc:
            print(
                f"Mailbox error while resetting node {node_id}: {exc}"
            )
            return False

        except (AttributeError, TypeError, ValueError) as exc:
            print(
                f"Invalid node or SDO value for node {node_id}: {exc}"
            )
            return False

    print(
        f"Error, reset fault deadline reached. "
        f"Node {node_id} could still be in fault."
    )

    return False

def PrintSW(node):
	print(f'Node {node.id} Statusword is:', hex(node.sdo['Statusword'].raw))

def CheckNotInFault(node, verbous = 1, blocking = 1):
	if node.sdo['Statusword'].raw & 0x8:
		if verbous == 0:
			return 0
		elif blocking:
			raise Exception(f'State01: Node {node.id} in fault!')
		elif verbous:
			print(f'Node {node.id} in fault')
	else:
		if verbous == 0:
			return 1
		else:
			print(f'Node {node.id} correctly not in fault')

def CheckInFault(node, verbous = 1, blocking = 1):
	if node.sdo['Statusword'].raw & 0x8:
		if verbous == 0:
			return 1
		else:
			print(f'Node {node.id} correctly in fault')
	else:
		if verbous == 0:
			return 0
		elif blocking:
			raise Exception(f'State01: Node {node.id} not in fault!')
		elif verbous:
			print(f'Node {node.id} not in fault')

def CheckNotInFault_fast(statusword):
	if statusword & 0x8:
		return False
	else:
		return True

def io_control (node, status):
	if status == 'ON':
		print('I/O ON')
		node.sdo.download(0x6200, 1, (1).to_bytes(1,'little'))
	else:
		print('I/O OFF')
		node.sdo.download(0x6200, 1, (0).to_bytes(1,'little'))
	time.sleep(0.05)

def is_eeprom_busy (node):
	if node.sdo[0x200A][0xb].raw == 0:
		return 0
	else:
		return 1

def check_deadline_expired (deadline_s, start_time, current_time):
	if current_time - start_time > deadline_s:
		return 1
	else:
		return 0

def write_current_user_data_to_eeprom(node, deadline_s=5.0):
	entry_time = time.perf_counter()
	start_time = entry_time


	while is_eeprom_busy(node) == 1:
		if check_deadline_expired(deadline_s,start_time,time.perf_counter()) == 1:
			print(f'Node {node} eeprom Busy or error, deadline reached, 0x200Asub8 is {node.sdo[0x200A][8].raw}')
			return
		time.sleep(0.05)

	node.sdo[0x200A][2].raw = 0x344e5854
	node.sdo[0x200A][3].raw = 4
	print('EEPROM writing started.')
	start_time=time.perf_counter()
	while is_eeprom_busy(node) == 1:
		if check_deadline_expired(deadline_s,start_time,time.perf_counter()) == 1:
			print(f'Node {node} eeprom Busy or error, deadline reached, 0x200Asub8 is {node.sdo[0x200A][8].raw}')
			return
		time.sleep(0.05)
	print (f'User data saved in memory, time execution: {time.perf_counter()-entry_time}')

states = {"not_ready_to_switch_on": {"mask": 0b11111111, "result": 0, "state_num": 1},
		  "switch_on_disabled": {"mask": 0b01001111, "result": 0b01000000, "state_num": 2},
		  "ready_to_switch_on": {"mask": 0b01101111, "result": 0b00100001, "state_num": 3},
		  "switched_on": {"mask": 0b01101111, "result": 0b00100011, "state_num": 4},
		  "operation_enabled": {"mask": 0b01101111, "result": 0b00100111, "state_num": 5},
		  "fault_reaction_active": {"mask": 0b01001111, "result": 0b00001111, "state_num": 9},
		  "fault": {"mask": 0b01001111, "result": 0b00001000, "state_num": 10}}

commands_to_op_en = {"not_ready_to_switch_on": None,
					 "switch_on_disabled": 6,
					 "ready_to_switch_on": 7,
					 "switched_on": 15,
					 "operation_enabled": None,
					 "fault_reaction_active": None,
					 "fault": 128}

def write_controlword(node, value, retries=3, delay=0.1):
    """
    Write Controlword with retry to avoid transient PacketError
    """
    data = int(value).to_bytes(2,'little')
    for attempt in range(1, retries+1):
        try:
            node.sdo["Controlword"].raw = value
            return
        except Exception as e:
            print(traceback.format_exc())
            print(f"[WARN] Controlword write retry {attempt}/{retries}: {e}")
            time.sleep(delay)
    raise RuntimeError(f"Failed to write Controlword after {retries} retries")

def get_sw(node, deadline: float = 1.0) -> int:
    entry_time = time.perf_counter()
    while check_deadline_expired(deadline, entry_time, time.perf_counter()) == 0:
        try:
            sw_bytes = node.sdo[0x6041].raw  # raw might be bytes
            sw = int.from_bytes(sw_bytes, 'little') if isinstance(sw_bytes, bytes) else int(sw_bytes)
            return sw
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("Timeout reading Statusword")

def go_to_op_enabled(node, deadline_s=5.0):
    entry_time = time.perf_counter()
    while check_deadline_expired(deadline_s, entry_time, time.perf_counter()) == 0:
        sw = get_sw(node, deadline_s)
        
        # Determine current DS402 state
        current_state = None
        for state, vals in states.items():
            if (sw & vals["mask"]) == vals["result"]:
                current_state = state
                break
        
        if current_state is None:
            print(f"[WARN] Unknown state, Statusword=0x{sw:04X}")
            time.sleep(0.05)
            continue
        
        print(f"Current state is {current_state}, Statusword=0x{sw:04X}")
        
        # Already Operation Enabled
        if current_state == "operation_enabled":
            return
        
        # Write next Controlword with retry
        cmd = commands_to_op_en.get(current_state)
        if cmd is not None:
            write_controlword(node, cmd)
            time.sleep(0.02)  # let the drive process the command
        
        time.sleep(0.01)

def go_to_switch_on_disabled(node, deadline_s=5.0):
    """
    Porta il nodo allo stato 'Switch On Disabled' (stato sicuro iniziale DS402).
    Gestisce eventuali fault e resetta lo stato se necessario.
    """
    entry_time = time.perf_counter()
    while check_deadline_expired(deadline_s, entry_time, time.perf_counter()) == 0:
        sw = get_sw(node, deadline_s)
        for state, vals in states.items():
            if (sw & vals["mask"]) == vals["result"]:
                current_state = state
                break

        print(f"Current state is {current_state}")

        # già nello stato desiderato
        if current_state == "switch_on_disabled":
            return

        # se in fault → resetta il fault
        elif current_state == "fault":
            node.sdo["Controlword"].raw = 128  # Fault reset (bit 7)
            time.sleep(0.05)

        # se in fault reaction active → attendi che termini
        elif current_state == "fault_reaction_active":
            time.sleep(0.05)

        # se in altri stati → disabilita con comando "Disable Voltage"
        else:
            node.sdo["Controlword"].raw = 0     # 0 = disable voltage
            time.sleep(0.05)

def read_statusword(node) -> int:
    """
    Reads the Statusword (0x6041) and returns it as an int.
    """
    sw_bytes = node.sdo.upload(0x6041, 0)
    return int.from_bytes(sw_bytes, byteorder='little')

def read_software_version(node) -> str:
    try:
        sv_bytes = node.sdo.upload(0x100A, 0)
        print(f"0x100A raw bytes: {sv_bytes}")
        sw = sv_bytes.decode("ascii", errors="ignore").rstrip("\x00")
        print(f"0x100A decoded   : '{sw}'")
        return sw
    except Exception as e:
        print(f"[WARN] Cannot read 0x100A:00 Software version: {repr(e)}")
        return ""



def fault_reset(node):
    """
    Resets the drive fault if present.
    Returns True if a reset command was sent.
    """
    sw = read_statusword(node)
    if sw & 0x08:  # Fault bit
        print(f"Fault detected. Statusword=0x{sw:04X}")
        node.sdo["Controlword"].raw = 0x80  # Fault Reset
        return True
    return False

def disable_drive(node):
    """
    Puts the drive in Switch On Disabled state.
    """
    node.sdo["Controlword"].raw = 0x00  # Disable voltage

def wait_switch_on_disabled(node, timeout=2.0) -> bool:
    """
    Polls Statusword until drive reaches Switch On Disabled or timeout.
    Returns True if successful.
    """
    mask = 0b01001111
    result = 0b01000000
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        sw = read_statusword(node)
        if (sw & 0x08) == 0 and (sw & mask) == result:
            return True
        time.sleep(0.05)
    return False

def reset_drive(node):
    """
    Performs a full reset:
    1. Sends Fault Reset if needed
    2. Disables the drive
    3. Waits until Switch On Disabled
    Returns True if drive successfully reached Switch On Disabled.
    """
    fault_reset(node)
    disable_drive(node)
    if wait_switch_on_disabled(node):
        print("Drive successfully reset to Switch On Disabled")
        return True
    else:
        sw = read_statusword(node)
        print(f"Reset failed, Statusword=0x{sw:04X}")
        return False

def configure_out_2_as_drive_ok(node):
	node.sdo[0x200b][8].raw = 1

def configure_out_polarity(node, polarity):
	if polarity:
		pol = 1
	else:
		pol = 0
	print(f"Set polarity to {pol}")
	node.sdo[0x200b][10].raw = pol


def erase_memory (node):
	node.sdo.download(0x200a,2,b'\x54\x58\x4e\x34')		#MF: PW
	node.sdo.download(0x200a,3,b'\x20\x00\x00\x00')
	while True:
		time.sleep(0.1)
		statusEEPROM = node.sdo.upload(0x200a, 8)
		statusEEPROMint = int.from_bytes(statusEEPROM,byteorder='little')
		if statusEEPROMint == 0:
			print('Memory Status is: ', statusEEPROMint, '---> Erase done, resetting node...')
			break
		else:
			print('Memory Status is: ', statusEEPROMint, '---> Waiting for erasing end...')


def erase_alarm_history(node):
	node.sdo[0x200A][2].raw = 0x344e5854
	node.sdo[0x200A][3].raw = 0x40
	while True:
		time.sleep(0.1)
		status_eeprom = node.sdo[0x200A][8].raw
		if status_eeprom == 0:
			print('Memory Status is: ', status_eeprom, '---> operation done...')
			break
		elif status_eeprom & 0xFFFFFC00:
			print('Error during operation, Memory status is: ', status_eeprom)
			break
		else:
			print('Memory Status is: ', status_eeprom, '---> Waiting for operation end...')

if __name__ == "__main__":
	network = initCANopen()
	# s60 = return_Node(network, 21)
	# print([hex(el) for el in ReadErrorsUntilFirstZero(s60)])
	# erase_alarm_history(s60)
	# for node_id in network:
	# 		if node_id==21:
	# 			s60=network[node_id]
	# QuitFromFaultCondition(s60)
	# go_to_op_enabled(s60)
	# print([hex(err) for err in ReadErrorsUntilFirstZero(s60)])
	# configure_out_2_as_drive_ok(s60)
	# while True:
	# 	configure_out_polarity(s60, 1)
	# 	time.sleep(3)
	# 	configure_out_polarity(s60, 0)
	# 	time.sleep(3)
	# if s60.sdo[0x200A][1].raw & 0x400: # MF: if NFC_ERROR_CRC_ERROR_HISTORY
	# 	print("CRC error history error. Erasing error history.")
	# 	erase_alarm_history(s60)

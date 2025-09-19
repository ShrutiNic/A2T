'''
Copyright 2024-2025 Accolade Electronics Pvt. Ltd

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

file        app_comm.py
brief       This is the source file for the UDS stack integration

date        01 Apr 2024
author      Accolade Electronics <www.accoladeelectronics.com>
'''

# For PCAN stack python modules
import os, sys
import copy
#sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uds_stack'))

########################################### (UDS over CAN: core initialization) ####################################################

import threading                
import time                     
from PCAN_UDS_2013 import *     
from Crypto.Cipher import AES   
import ctypes
from ctypes import create_string_buffer, byref
from tkinter import ttk, filedialog, messagebox
import app_ui

# A global counter to keep track of the number of failed tests (see display_uds_msg function)
g_nbErr = 0

# import the dlls required for stack
from pathlib import Path

# dll_path = Path(__file__).resolve().parent /'uds_stack'
# sys.path.insert(0, str(dll_path))
#os.add_dll_directory(str(dll_path))

objPCANUds = PCAN_UDS_2013()

g_pcan_handle = PCANTP_HANDLE_USBBUS1
g_pcan_config = uds_msgconfig()
source_mapping = uds_mapping()
response_mapping = uds_mapping()

def test_result_to_string(test):
    return 'Success' if test else 'Fail'

def print_test_status(test):
    return test_result_to_string(objPCANUds.StatusIsOk_2013(test, PUDS_STATUS_OK, False))

# def can_init(can_fd, bit_rate, tester_id, ecu_id, nai_protocol):
#     # print(f'app_comm  : bit_rate              : {bit_rate}')
#     # print(f'app_comm  : tester_id             : {tester_id:X}')
#     # print(f'app_comm  : ecu_id                : {ecu_id:X}')
#     # print(f'app_comm  : iso_tp_addressing_mode: {nai_protocol}')
#
#     print(f'app_comm  : bit_rate              : {bit_rate}')
#     print(f'app_comm  : tester_id             : {tester_id}')
#     print(f'app_comm  : ecu_id                : {ecu_id}')
#     print(f'app_comm  : iso_tp_addressing_mode: {nai_protocol}')
#
#     ecu_id = int(ecu_id, 16)
#     tester_id = int(tester_id, 16)
#     buff_size = 256
#     buffer = create_string_buffer(buff_size)
#     status = objPCANUds.GetValue_2013(PCANTP_HANDLE_NONEBUS, PUDS_PARAMETER_API_VERSION, buffer, buff_size)
#     print('app_comm  : PCAN-UDS API Version - %s: %s' % (buffer.value, print_test_status(status)))
#
#     if can_fd == 'CAN_FD':
#         # PCAN_BITRATE_SAE_J2284_4 = create_string_buffer(b'f_clock=80000000,nom_brp=2,nom_tseg1=63,nom_tseg2=16,' \
#         #                                                     'nom_sjw=16,data_brp=2,data_tseg1=15,data_tseg2=4,data_sjw=4')
#         # status = objPCANUds.InitializeFD_2013(g_pcan_handle, PCAN_BITRATE_SAE_J2284_4)
#         PCAN_BITRATE_SAE_J2284_4 = create_string_buffer(b'f_clock=80000000,nom_brp=10,nom_tseg1=12,nom_tseg2=3,'
#                                                             b'nom_sjw=1,data_brp=10,data_tseg1=5,data_tseg2=2,data_sjw=1'
#                                                         )
#         status = objPCANUds.InitializeFD_2013(g_pcan_handle, PCAN_BITRATE_SAE_J2284_4)
#
#     else:
#         if bit_rate == '250Kbps':
#             status = objPCANUds.Initialize_2013(g_pcan_handle, PCANTP_BAUDRATE_250K, 0, 0, 0)
#         if bit_rate == '500Kbps':
#             status = objPCANUds.Initialize_2013(g_pcan_handle, PCANTP_BAUDRATE_500K, 0, 0, 0)
#         if bit_rate == '1Mbps':
#             status = objPCANUds.Initialize_2013(g_pcan_handle, PCANTP_BAUDRATE_1M, 0, 0, 0)
#     print('app_comm  : Initialize channel: %s' % (print_test_status(status)))
#
#     if print_test_status(status) == 'Fail':
#         return False
#
#     timeout_request = c_uint32(0)
#     status = objPCANUds.GetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_REQUEST, timeout_request,
#                                     sizeof(timeout_request))
#     print('app_comm  : Get request timeout value (%ums): %s' % (timeout_request.value, print_test_status(status)))
#
#     customTimeOut = c_uint32(timeout_request.value * 2)
#     status = objPCANUds.SetValue_2013(g_pcan_handle,
#                                     PUDS_PARAMETER_TIMEOUT_REQUEST,
#                                     customTimeOut, sizeof(customTimeOut))
#     print('app_comm  : Set request timeout value (%ums): %s' % (customTimeOut.value, print_test_status(status)))
#
#     status = objPCANUds.GetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_REQUEST, timeout_request,
#                                     sizeof(timeout_request))
#     print('app_comm  : Get request timeout value (%ums): %s' % (timeout_request.value, print_test_status(status)))
#
#     timeout_response = c_uint32(0)
#     status = objPCANUds.GetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_RESPONSE, timeout_response,
#                                     sizeof(timeout_response))
#     print('app_comm  : Get response timeout value (%ums): %s' % (timeout_response.value, print_test_status(status)))
#
#     customTimeOut = c_uint32(timeout_response.value * 2)
#     status = objPCANUds.SetValue_2013(g_pcan_handle,
#                                     PUDS_PARAMETER_TIMEOUT_RESPONSE,
#                                     customTimeOut, sizeof(customTimeOut))
#     print('app_comm  : Set response timeout value (%ums): %s' % (customTimeOut.value, print_test_status(status)))
#     status = objPCANUds.GetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_RESPONSE, timeout_response,
#                                     sizeof(timeout_response))
#     print('app_comm  : Get response timeout value (%ums): %s' % (timeout_response.value, print_test_status(status)))
#
#     g_pcan_config.can_id = ecu_id
#     g_pcan_config.can_msgtype = PCANTP_CAN_MSGTYPE_STANDARD
#     if nai_protocol == 'PUDS_MSGPROTOCOL_ISO_15765_2_29B_NORMAL':
#         g_pcan_config.nai.protocol = PUDS_MSGPROTOCOL_ISO_15765_2_29B_NORMAL
#     elif nai_protocol == 'PUDS_MSGPROTOCOL_ISO_15765_2_11B_NORMAL':
#         g_pcan_config.nai.protocol = '11B_FIXED_NORMAL'
#     else:
#         g_pcan_config.nai.protocol = PUDS_MSGPROTOCOL_ISO_15765_2_29B_NORMAL
#     g_pcan_config.nai.target_type = PCANTP_ISOTP_ADDRESSING_PHYSICAL
#     g_pcan_config.type = PUDS_MSGTYPE_USDT
#     g_pcan_config.nai.source_addr = 0x726
#     g_pcan_config.nai.target_addr = 0x72E
#
#     # Initialize source mapping
#     source_mapping.can_id = ecu_id
#     source_mapping.can_id_flow_ctrl = tester_id
#     source_mapping.can_msgtype = g_pcan_config.can_msgtype
#     source_mapping.can_tx_dlc = 8
#     source_mapping.nai = copy.deepcopy(g_pcan_config.nai)
#
#     # Initialize response mapping
#     response_mapping.can_id = source_mapping.can_id_flow_ctrl
#     response_mapping.can_id_flow_ctrl = source_mapping.can_id
#     response_mapping.can_msgtype = source_mapping.can_msgtype
#     response_mapping.can_tx_dlc = source_mapping.can_tx_dlc
#     response_mapping.nai = copy.deepcopy(source_mapping.nai)
#     response_mapping.nai.source_addr = source_mapping.nai.target_addr
#     response_mapping.nai.target_addr = source_mapping.nai.source_addr
#
#     # Add mappings on transmitter
#     status = objPCANUds.AddMapping_2013(g_pcan_handle, source_mapping)
#     print("Add source mapping on transmitter: %s" %(print_test_status(status)))
#     status = objPCANUds.AddMapping_2013(g_pcan_handle, response_mapping)
#     print("Add response mapping on transmitter: %s" %(print_test_status(status)))
#
#     print(f'app_comm  : PCAN initialized with bit rate {bit_rate}, server id {hex(tester_id)}, client id {hex(ecu_id)}')
#     return True


def can_init(can_fd, bit_rate, tester_id, ecu_id, nai_protocol):
    print(f'app_comm  : bit_rate              : {bit_rate}')
    print(f'app_comm  : tester_id             : {tester_id}')
    print(f'app_comm  : ecu_id                : {ecu_id}')
    print(f'app_comm  : iso_tp_addressing_mode: {nai_protocol}')

    # Convert IDs from hex strings to int
    ecu_id = int(ecu_id, 16)
    tester_id = int(tester_id, 16)

    # Get PCAN-UDS API version
    buff_size = 256
    buffer = create_string_buffer(buff_size)
    status = objPCANUds.GetValue_2013(PCANTP_HANDLE_NONEBUS, PUDS_PARAMETER_API_VERSION, buffer, buff_size)
    print('app_comm  : PCAN-UDS API Version - %s: %s' % (buffer.value, print_test_status(status)))

    # Initialize the PCAN channel
    if can_fd == 'CAN_FD':
        bitrate_str = b'f_clock=80000000,nom_brp=10,nom_tseg1=12,nom_tseg2=3,nom_sjw=1,data_brp=10,data_tseg1=5,data_tseg2=2,data_sjw=1'
        PCAN_BITRATE = create_string_buffer(bitrate_str)
        status = objPCANUds.InitializeFD_2013(g_pcan_handle, PCAN_BITRATE)
    else:
        if bit_rate == '250Kbps':
            status = objPCANUds.Initialize_2013(g_pcan_handle, PCANTP_BAUDRATE_250K, 0, 0, 0)
        elif bit_rate == '500Kbps':
            status = objPCANUds.Initialize_2013(g_pcan_handle, PCANTP_BAUDRATE_500K, 0, 0, 0)
        elif bit_rate == '1Mbps':
            status = objPCANUds.Initialize_2013(g_pcan_handle, PCANTP_BAUDRATE_1M, 0, 0, 0)
    print('app_comm  : Initialize channel: %s' % print_test_status(status))

    if print_test_status(status) == 'Fail':
        return False

    # Timeout handling
    timeout_request = c_uint32(0)
    objPCANUds.GetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_REQUEST, timeout_request, sizeof(timeout_request))
    customTimeOut = c_uint32(timeout_request.value * 2)
    objPCANUds.SetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_REQUEST, customTimeOut, sizeof(customTimeOut))

    timeout_response = c_uint32(0)
    objPCANUds.GetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_RESPONSE, timeout_response, sizeof(timeout_response))
    customTimeOut = c_uint32(timeout_response.value * 2)
    objPCANUds.SetValue_2013(g_pcan_handle, PUDS_PARAMETER_TIMEOUT_RESPONSE, customTimeOut, sizeof(customTimeOut))

    # === PCAN Configuration ===
    g_pcan_config.can_id = ecu_id
    g_pcan_config.type = PUDS_MSGTYPE_USDT

    # Detect protocol type
    nai_protocol_upper = nai_protocol.strip().upper()

    if nai_protocol_upper in ['29B_NORMAL', 'PUDS_MSGPROTOCOL_ISO_15765_2_29B_NORMAL']:
        g_pcan_config.can_msgtype = PCANTP_CAN_MSGTYPE_EXTENDED
        g_pcan_config.nai.protocol = PUDS_MSGPROTOCOL_ISO_15765_2_29B_NORMAL
    elif nai_protocol_upper in ['11B_NORMAL', '11B_FIXED_NORMAL', 'PUDS_MSGPROTOCOL_ISO_15765_2_11B_NORMAL']:
        g_pcan_config.can_msgtype = PCANTP_CAN_MSGTYPE_STANDARD
        g_pcan_config.nai.protocol = PUDS_MSGPROTOCOL_ISO_15765_2_11B_NORMAL
    else:
        print(f"Unsupported protocol mode: {nai_protocol}")
        return False

    g_pcan_config.nai.target_type = PCANTP_ISOTP_ADDRESSING_PHYSICAL
    g_pcan_config.nai.source_addr = 0  # Not used in 11B/29B normal modes
    g_pcan_config.nai.target_addr = 0

    # === Source Mapping ===
    source_mapping.can_id = ecu_id
    source_mapping.can_id_flow_ctrl = tester_id
    source_mapping.can_msgtype = g_pcan_config.can_msgtype
    source_mapping.can_tx_dlc = 8
    source_mapping.nai = copy.deepcopy(g_pcan_config.nai)

    # === Response Mapping ===
    response_mapping.can_id = tester_id
    response_mapping.can_id_flow_ctrl = ecu_id
    response_mapping.can_msgtype = g_pcan_config.can_msgtype
    response_mapping.can_tx_dlc = 8
    response_mapping.nai = copy.deepcopy(g_pcan_config.nai)

    # Add source and response mappings
    status = objPCANUds.AddMapping_2013(g_pcan_handle, source_mapping)
    print("Add source mapping on transmitter: %s" % print_test_status(status))

    status = objPCANUds.AddMapping_2013(g_pcan_handle, response_mapping)
    print("Add response mapping on transmitter: %s" % print_test_status(status))

    print(f'app_comm  : PCAN initialized with bit rate {bit_rate}, server id {hex(tester_id)}, client id {hex(ecu_id)}')
    return True



########################################### (UDS over CAN: service tests) ####################################################

g_file_path = ''
g_file_size = 0

def test_read_write_did(handle, config, did, update_did_widget):
    print(f"\nTesting DID: {hex(did)}")
    response_data, is_valid = testReadDataByIdentifier(handle, config, did)
    if response_data and is_valid:
        print(f"app_comm: Read data by ID succeeded for DID: {hex(did)}")
        print(f"Response Data for DID {hex(did)}: {response_data['response']}")
        raw_data = response_data['response'][3:]
        print(f"Processed Raw Data for DID {hex(did)}: {raw_data}")
        update_did_widget(did, raw_data)
        return raw_data
    else:
        print(f"app_comm: Read data by ID test failed for DID: {hex(did)}")
        error_type = response_data.get("type", "Unknown") if response_data else "Unknown"
        print(f"Error Type: {error_type}")
    return None  


def startRoutine(g_project):
    handle = g_pcan_handle
    config = g_pcan_config
    response_data, is_valid = testDiagnosticSessionControl(handle, config, g_project["session"])
    print(f"Diagnostic Session Control Response: {response_data['type']}")
    if not is_valid:
        print("Diagnostic Session Control failed!")
        return response_data, False 
    response_data, is_valid = testSecurityAccess(handle, config, g_project["security"])
    print(f"Security Access Response: {response_data['type']}")
    if not is_valid:
        print("Security Access failed!")
        return response_data, False  
    return response_data, True  

def startRoutineCert(selected_files_result):

    handle = g_pcan_handle
    config = g_pcan_config

    response_data, is_valid = testDiagnosticSessionControlCert(handle, config)

    print(f"Diagnostic Session Control Response: {response_data['type']}")
    if not is_valid:
        print("Diagnostic Session Control failed!")
        messagebox.showinfo("Diagnostic session failed", f"Diagnostic Session Control failed!")
        return response_data, False
    security = "AES128"
    response_data, is_valid = testSecurityAccess(handle, config, security)
    print(f"Security Access Response: {response_data['type']}")
    if not is_valid:
        print("Security Access failed!")
        messagebox.showinfo("Security Access failed", f"Security Access failed!")
        return response_data, False  
    if not selected_files_result:
        print("Error: No files selected. Please select files first.")
        return
    response_data, is_valid = testTrasferFile(handle, config, selected_files_result)
    if not is_valid:
        print("transfer file failed!")
        return response_data, False  
    print("All services executed successfully!", response_data)
    return response_data, True  





def startRoutineConfig(security):
    handle = g_pcan_handle
    config = g_pcan_config
    response_data, is_valid = testDiagnosticSessionControlConfig(handle, config)
    print(f"Diagnostic Session Control Response: {response_data}, {config}, {handle}")
    if not is_valid:
        print("Diagnostic Session Control failed!")
        messagebox.showinfo("Diagnostic session failed", f"Diagnostic Session Control failed!")
        return response_data, False  
    response_data, is_valid = testSecurityAccess(handle, config, security)
    print(f"Security Access Response: {response_data['type']}")
    if not is_valid:
        print("Security Access failed!")
        messagebox.showinfo("Security Access failed", f"Security Access failed!")
        return response_data, False  
    # response_data, is_valid = testRoutineControlCrcConfig(handle, config)
    # print(f"Routine Control Response: {response_data['type']}")
    # if not is_valid:
    #     print("Routine Control failed!")
    #     return response_data, False  
    messagebox.showinfo("Config Reset", f"The configuration reset is successful !")
    return response_data, True

def startRoutineConfig_aepl(security):
    handle = g_pcan_handle
    config = g_pcan_config
    response_data, is_valid = testDiagnosticSessionControlConfig_aepl(handle, config)
    print(f"Diagnostic Session Control Response: {response_data['type']}")
    if not is_valid:
        print("Diagnostic Session Control failed!")
        messagebox.showinfo("Diagnostic session failed", f"Diagnostic Session Control failed!")
        return response_data, False
    print("Security",security)  
    response_data, is_valid = testSecurityAccess(handle, config, security)
    print(f"Security Access Response: {response_data['type']}")
    if not is_valid:
        print("Security Access failed!")
        messagebox.showinfo("Security Access failed", f"Security Access failed!")
        return response_data, False  
    # response_data, is_valid = testRoutineControlCrcConfig(handle, config)
    # print(f"Routine Control Response: {response_data['type']}")
    # if not is_valid:
    #     print("Routine Control failed!")
    #     return response_data, False  
    messagebox.showinfo("Config Reset", f"The configuration reset is successful !")
    return response_data, True

def test_pgn_config_did(did, hex_value):
    try:
        response_data, is_valid = testWriteDataByIdentifier(g_pcan_handle, g_pcan_config, did, hex_value, len(hex_value))
        print(f"Routine Control Response: {response_data['type']}")
        testECUReset(g_pcan_handle, g_pcan_config)
        return response_data
    except ValueError as e:
        print(f"Error converting hex value for DID {hex(did)}: {e}")
        return {"type": "Negative", "did": hex(did), "hex_value": hex_value, "error": f"Error converting hex value: {str(e)}"}


# def test_write_did(did, hex_value):
#     if isinstance(did, str):
#         try:
#             did = int(did, 16)  
#         except ValueError as e:
#             print(f"Error: Invalid DID value '{did}', cannot convert to integer.")
#             return {"type": "Negative", "error": f"Invalid DID: {did}"}
#     try:
#         hex_value = hex_value.replace(" ", "")  
#         int(hex_value, 16)  
#     except ValueError as e:
#         print(f"Error: Invalid hex value '{hex_value}', must be a valid hexadecimal string.")
#         return {"type": "Negative", "error": f"Invalid hex value: {hex_value}"}
#     if len(hex_value) % 2 != 0:
#         hex_value = "0" + hex_value
#     print(f"Preparing to write DID: {hex(did)}")  
#     print(f"Hex value to be written: {hex_value}")
#     try:
#         data_record = bytearray.fromhex(hex_value)
#         data_record_size = len(data_record)
#         print(f"Data record size: {data_record_size}")
#         print(f"Data record: {data_record.hex()}")
#         did_bytes = did.to_bytes(2, byteorder='big')  
#         print(f"Processed DID (2 bytes): {int.from_bytes(did_bytes, 'big')}")  
#         print("DID is:", did_bytes.hex())  
#         response_data, is_valid = testWriteDataByIdentifier(g_pcan_handle, g_pcan_config, did, data_record, data_record_size)
#         print("testWriteDataByIdentifier",g_pcan_handle, g_pcan_config, did, data_record, data_record_size)
#         print(f"Routine Control Response: {response_data['type']}")
#         return response_data
#     except ValueError as e:
#         print(f"Error converting hex value for DID {hex(did)}: {e}")
#         return {"type": "Negative", "did": hex(did), "hex_value": hex_value, "error": f"Error converting hex value: {str(e)}"}

def test_write_did(did, hex_value):
    """
    Sends a UDS WriteDataByIdentifier (0x2E) request to the ECU.

    Parameters:
        did (str or int): Data Identifier (e.g., '5497' or 0x5497).
        hex_value (str): Hex string or ASCII to be written (e.g., '22222222').

    Returns:
        dict: Contains response type, display value, and raw response data.
    """

    # Step 1: Convert DID to integer if it's a string
    if isinstance(did, str):
        try:
            did = int(did, 16)
        except ValueError:
            error_msg = f"Invalid DID value '{did}', cannot convert to integer."
            print(f"[ERROR] {error_msg}")
            return {"type": "Negative", "error": error_msg}

    # Step 2: Clean and validate the hex_value input
    original_input = hex_value
    hex_value = hex_value.replace(" ", "")  # Remove spaces

    was_ascii_converted = False
    try:
        # Try parsing it as a hex string
        int(hex_value, 16)
    except ValueError:
        try:
            # Try converting from ASCII to hex
            hex_value = original_input.encode("ascii").hex()
            was_ascii_converted = True
            print(f"[INFO] Converted ASCII to hex: '{original_input}' -> {hex_value}")
        except UnicodeEncodeError:
            error_msg = f"Invalid input: not hex and not valid ASCII: '{original_input}'"
            print(f"[ERROR] {error_msg}")
            return {"type": "Negative", "error": error_msg}

    # Step 3: Ensure even-length hex string
    if len(hex_value) % 2 != 0:
        hex_value = "0" + hex_value
        print(f"[INFO] Padded hex to even length: {hex_value}")

    # Step 4: Convert to bytearray
    try:
        data_record = bytearray.fromhex(hex_value)
    except ValueError as e:
        error_msg = f"Cannot convert hex to bytes: {e}"
        print(f"[ERROR] {error_msg}")
        return {"type": "Negative", "error": error_msg}

    data_record_size = len(data_record)

    if data_record_size == 0:
        error_msg = "Payload is empty after processing. Nothing to write."
        print(f"[ERROR] {error_msg}")
        return {"type": "Negative", "error": error_msg}

    # Step 5: Logging details
    print(f"[INFO] Preparing to write DID: 0x{did:04X}")
    print(f"[INFO] Hex value to be written: {hex_value}")
    print(f"[INFO] Data record size: {data_record_size}")
    print(f"[INFO] Data record (hex): {data_record.hex()}")

    # Step 6: Convert DID to 2-byte format
    try:
        did_bytes = did.to_bytes(2, byteorder='big')
        print(f"[DEBUG] Processed DID (2 bytes): {did_bytes.hex()}")
    except OverflowError:
        error_msg = f"DID value {did} is too large to fit in 2 bytes."
        print(f"[ERROR] {error_msg}")
        return {"type": "Negative", "error": error_msg}

    # Step 7: Send WDBI request
    try:
        response_data, is_valid = testWriteDataByIdentifier(
            g_pcan_handle,
            g_pcan_config,
            did,
            data_record,
            data_record_size
        )

        display_value = original_input if was_ascii_converted else hex_value

        if response_data['type'] == "Negative":
            print(f"[ERROR] ECU rejected WriteDataByIdentifier for DID 0x{did:04X}")
            print(f"[DEBUG] Response: {response_data.get('response')}")
        else:
            print(f"[SUCCESS] WriteDataByIdentifier for DID 0x{did:04X} succeeded.")

        response_data["display_value"] = display_value
        return response_data

    except Exception as e:
        error_msg = f"Exception during WriteDataByIdentifier: {e}"
        print(f"[ERROR] {error_msg}")
        return {"type": "Negative", "error": error_msg}






def testDiagnosticSessionControl(channel, config, session):
    request = uds_msg()
    response = uds_msg()
    session_info = uds_sessioninfo()
    confirmation = uds_msg()
    
    status = objPCANUds.SvcDiagnosticSessionControl_2013(channel, config, request, session)
    print('Execute Diagnostic Session Control service: %s' % (print_test_status(status)))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: DiagnosticSessionControl: ' + test_result_to_string(result))
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result

def testDiagnosticSessionControlCert(channel, config):
    request = uds_msg()
    response = uds_msg()
    session_info = uds_sessioninfo()
    confirmation = uds_msg()
    status = objPCANUds.SvcDiagnosticSessionControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_DSC_ECUPS2)
    print('Execute Diagnostic Session Control service: %s' % (print_test_status(status)))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: DiagnosticSessionControl: ' + test_result_to_string(result))
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result

def testDiagnosticSessionControlConfig(channel, config):
    request = uds_msg()
    response = uds_msg()
    session_info = uds_sessioninfo()
    confirmation = uds_msg()

    status = objPCANUds.SvcDiagnosticSessionControl_2013(
        channel, config, request, objPCANUds.PUDS_SVC_PARAM_DSC_ECUEDS3
    )
    print('Execute Diagnostic Session Control service: %s' % print_test_status(status))
    print("Channel in diagnostic session", channel)
    print("PUDS_SVC_PARAM_DSC_ECUEDS3",objPCANUds.PUDS_SVC_PARAM_DSC_ECUEDS3)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)

    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: DiagnosticSessionControl: ' + test_result_to_string(result))

    objPCANUds.MsgFree_2013(request)
    objPCANUds.MsgFree_2013(response)
    objPCANUds.MsgFree_2013(confirmation)

    return result


def testDiagnosticSessionControlConfig_aepl(channel, config):
    request = uds_msg()
    response = uds_msg()
    session_info = uds_sessioninfo()
    confirmation = uds_msg()

    status = objPCANUds.SvcDiagnosticSessionControl_2013(
        channel, config, request, objPCANUds.PUDS_SVC_PARAM_DSC_ECUPS
    )
    print("PUDS_SVC_PARAM_DSC_ECUPS",objPCANUds.PUDS_SVC_PARAM_DSC_ECUPS)
    print('Execute Diagnostic Session Control service: %s' % print_test_status(status))

    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)

    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: DiagnosticSessionControl: ' + test_result_to_string(result))

    objPCANUds.MsgFree_2013(request)
    objPCANUds.MsgFree_2013(response)
    objPCANUds.MsgFree_2013(confirmation)

    return result

    





# def aes_128_encrypt(key, security_access_data):
#     cipher = AES.new(key, AES.MODE_ECB)
#     ciphertext_bytes = cipher.encrypt(security_access_data)
#     return ciphertext_bytes

def aes_128_encrypt(key: bytes, seed_buffer: ctypes.Array) -> bytes:
    """
    Encrypt the 16-byte seed buffer using AES-128 ECB mode.

    Args:
        key (bytes): 16-byte AES key.
        seed_buffer (ctypes.Array): ctypes buffer containing 16 bytes.

    Returns:
        bytes: AES-encrypted 16-byte ciphertext.
    """
    # Extract raw bytes from ctypes buffer
    seed_bytes = bytes(seed_buffer.raw[:16])  # Ensure only 16 bytes used
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext_bytes = cipher.encrypt(seed_bytes)
    return ciphertext_bytes

# def testSecurityAccess(channel, config, security):
#     request = uds_msg()
#     response = uds_msg()
#     confirmation = uds_msg()

#     result = False
#     diagnostic_session_key =bytearray(4)
#     print(f"Security Access : {security}")

#     # Set seed length
#     seed_length = 16 if security == "AES128" else 4
#     security_access_data = ctypes.create_string_buffer(seed_length)

#     # Step 1: Request seed
#     status = objPCANUds.SvcSecurityAccess_2013(
#         channel,
#         config,
#         request,
#         objPCANUds.PUDS_SVC_PARAM_SA_RSD_1,
#         security_access_data,
#         0
#     )

#     if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
#         status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
#     print('UDS_SvcSecurityAccess_2013: %i' % (status.value))

#     if not objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
#         _, result = display_uds_msg_validate(request, None, False)
#         cleanup_msgs(request, response, confirmation)
#         return {"request": request, "response": response, "type": "Negative"}, result

#     # Step 2: Extract seed
#     for i in range(seed_length):
#         security_access_data[i] = response.msg.msgdata.any.contents.data[2 + i]

#     # Step 3: Generate key based on method
#     if security == "AES128":
#         key = b'TCATMVCC2BLU5UEE'
#         print("in test security access", key)
#         diagnostic_session_key = aes_128_encrypt(key, security_access_data)
#     elif security == "XOR":
#         diagnostic_session_key[0] = security_access_data[0:1][0] ^ 0xAA
#         diagnostic_session_key[1] = security_access_data[1:2][0] ^ 0xAA  # High byte
#         diagnostic_session_key[2] = security_access_data[2:3][0] ^ 0xAA
#         diagnostic_session_key[3] = security_access_data[3:4][0] ^ 0xAA
#     else:
#         print("Unsupported Security Method")
#         cleanup_msgs(request, response, confirmation)
#         return {"request": request, "response": response, "type": "Negative"}, False

#     # Step 4: Write the generated key into buffer
#     for i in range(seed_length):
#         security_access_data[i] = diagnostic_session_key[i]

#     # Step 5: Validate seed response
#     _, result = display_uds_msg_validate(confirmation, response, False)
#     status = objPCANUds.MsgFree_2013(request)

#     status = objPCANUds.MsgFree_2013(response)

#     status = objPCANUds.MsgFree_2013(confirmation)
 
#     print('result :',result)
#     # Step 6: Send key
#     if result:
#         status = objPCANUds.SvcSecurityAccess_2013(
#             channel,
#             config,
#             request,
#             objPCANUds.PUDS_SVC_PARAM_SA_SK_2,
#             security_access_data,
#             ctypes.sizeof(security_access_data)
#         )
#         if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
#             status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
#             print('UDS_SvcSecurityAccess_2013: %i' % (status.value))
#             if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
#                 _, result = display_uds_msg_validate(confirmation, response, False)
#             else:
#                 _, result = display_uds_msg_validate(request, None, False)

#     print('UDS Service: SecurityAccess: ' + test_result_to_string(result))

#     #cleanup_msgs(request, response, confirmation)

#     return {"request": request, "response": response, "type": "Positive" if result else "Negative"}, result

def testSecurityAccess(channel, config, security):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()

    result = False
    diagnostic_session_key = bytearray(16)
    print(f"Security Access : {security}")

    # Set seed length
    seed_length = 16 if security == "AES128" else 4
    security_access_data = ctypes.create_string_buffer(seed_length)

    # Step 1: Request seed
    status = objPCANUds.SvcSecurityAccess_2013(
        channel,
        config,
        request,
        objPCANUds.PUDS_SVC_PARAM_SA_RSD_1,
        security_access_data,
        0
    )

    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print('UDS_SvcSecurityAccess_2013: %i' % (status.value))

    if not objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        _, result = display_uds_msg_validate(request, None, False)
        cleanup_msgs(request, response, confirmation)
        return {"request": request, "response": response, "type": "Negative"}, result

    # Step 2: Extract seed from response
    for i in range(seed_length):
        security_access_data[i] = response.msg.msgdata.any.contents.data[2 + i]

    # Step 3: Generate key
    if security == "AES128":
        key = b'TCATMVCC2BLU5UEE'
        print("in test security access", key)

        # ✅ FIXED: aes_128_encrypt returns bytes, not a ctypes buffer
        encrypted_key = aes_128_encrypt(key, security_access_data)

        # Copy bytes into diagnostic_session_key
        for i in range(seed_length):
            diagnostic_session_key[i] = encrypted_key[i]

    elif security == "XOR":
        diagnostic_session_key[0] = security_access_data[0] ^ 0xAA
        diagnostic_session_key[1] = security_access_data[1] ^ 0xAA
        diagnostic_session_key[2] = security_access_data[2] ^ 0xAA
        diagnostic_session_key[3] = security_access_data[3] ^ 0xAA
    else:
        print("Unsupported Security Method")
        cleanup_msgs(request, response, confirmation)
        return {"request": request, "response": response, "type": "Negative"}, False

    # Step 4: Copy generated key to buffer
    for i in range(seed_length):
        security_access_data[i] = diagnostic_session_key[i]

    # Step 5: Validate seed response
    _, result = display_uds_msg_validate(confirmation, response, False)
    objPCANUds.MsgFree_2013(request)
    objPCANUds.MsgFree_2013(response)
    objPCANUds.MsgFree_2013(confirmation)

    print('result :', result)

    # Step 6: Send key
    if result:
        status = objPCANUds.SvcSecurityAccess_2013(
            channel,
            config,
            request,
            objPCANUds.PUDS_SVC_PARAM_SA_SK_2,
            security_access_data,
            ctypes.sizeof(security_access_data)
        )

        if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
            status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
            print('UDS_SvcSecurityAccess_2013: %i' % (status.value))
            if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
                _, result = display_uds_msg_validate(confirmation, response, False)
            else:
                _, result = display_uds_msg_validate(request, None, False)

    print('UDS Service: SecurityAccess: ' + test_result_to_string(result))
    return {"request": request, "response": response, "type": "Positive" if result else "Negative"}, result

def cleanup_msgs(*msgs):
    for msg in msgs:
        objPCANUds.MsgFree_2013(msg)

def testRoutineControlCrcCheck(channel, config, config_type_byte):
    routine_control_option_record = create_string_buffer(2)
    routine_control_option_record_size = 2
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = False
    print('\n\n*** UDS Service: RoutineControl Erasing Flash***')
    routine_control_option_record_size =1
    for i in range(6):
        routine_control_option_record[0] = config_type_byte
    status = objPCANUds.SvcRoutineControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_STR, 0xFD02,
                                                routine_control_option_record, routine_control_option_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
         status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Result: %i' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: RoutineControl Erasing Flash: ' + test_result_to_string(result))
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result

def testRoutineControlCrcConfig(channel, config):
    routine_control_option_record = create_string_buffer(2)
    routine_control_option_record_size = 2
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = False
    print('\n\n*** UDS Service: RoutineControl Erasing Flash***')
    routine_control_option_record_size =1
    for i in range(6):
        routine_control_option_record[0] = 0x0
    status = objPCANUds.SvcRoutineControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_STR, 0xFD01,
                                                routine_control_option_record, routine_control_option_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
         status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Result: %i' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: RoutineControl Erasing Flash: ' + test_result_to_string(result))
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result

def testRoutineControlCrcCheckCert(channel, config, select_files_result, sequence_number, crc32_value):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = False
    print('\n\n*** UDS Service: RoutineControl Erasing Flash***')
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    if not select_files_result:
        print("Error: No file data provided.")
        return None, False  
    all_files_data = select_files_result.get("all_files_data", [])
    file_sizes = [int(file["file_size"], 16) for file in all_files_data]
    routine_control_option_record_size = 6 + (4 * len(file_sizes))  
    routine_control_option_record = create_string_buffer(routine_control_option_record_size)
    routine_control_option_record[0] = sequence_number & 0xFF
    routine_control_option_record[1] = (crc32_value >> 24) & 0xFF  
    routine_control_option_record[2] = (crc32_value >> 16) & 0xFF
    routine_control_option_record[3] = (crc32_value >> 8) & 0xFF
    routine_control_option_record[4] = (crc32_value >> 0) & 0xFF  
    routine_control_option_record[5] = len(file_sizes) & 0xFF
    offset = 6  
    for file_size in file_sizes:
        routine_control_option_record[offset + 0] = (file_size >> 24) & 0xFF  
        routine_control_option_record[offset + 1] = (file_size >> 16) & 0xFF
        routine_control_option_record[offset + 2] = (file_size >> 8) & 0xFF
        routine_control_option_record[offset + 3] = (file_size >> 0) & 0xFF  
        offset += 4
    print('\n\n*** UDS Service: RoutineControl Erasing Flash***')
    status = objPCANUds.SvcRoutineControl_2013(
        channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_STR, 0xFF00,
        routine_control_option_record, routine_control_option_record_size
    )
    #print('UDS Service: RequestDownload: ' + test_result_to_string(result))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Result: %i' % (status.value))
    if not select_files_result:
        print("Error: No file data provided.")
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
        return None, False
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: RoutineControl Erasing Flash: ' + test_result_to_string(result))
    all_files_data = select_files_result.get("all_files_data", [])
    file_sizes = [int(file["file_size"], 16) for file in all_files_data]
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    response_data = {
        "request": request,
        "response": response,
        "type": "Positive" if result else "Negative"
    }
    return response_data, result 

def testReadDataByIdentifier(channel, config, did):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = None
    print('\n\n*** UDS Service: ReadDataByIdentifier ***')
    data_identifier = c_uint16(did)
    # print("Did in read data", did)
    status = objPCANUds.SvcReadDataByIdentifier_2013(channel, config, request, data_identifier, 1)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print('UDS_SvcReadDataByIdentifier_2013: %x' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: ReadDataByIdentifier [{}]: {}'.format(hex(did), test_result_to_string(result)))
    objPCANUds.MsgFree_2013(request)
    objPCANUds.MsgFree_2013(response)
    objPCANUds.MsgFree_2013(confirmation)
    return result

def testWriteDataByIdentifier(channel, config, did, data_record, data_record_size):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    data_record_ctypes = ctypes.create_string_buffer(bytes(data_record))
    print('\n\nSends a physical WriteDataByIdentifier message: ')
    status = objPCANUds.SvcWriteDataByIdentifier_2013(channel, config, request, did, data_record_ctypes, data_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(f'UDS_SvcWriteDataByIdentifier_2013: {status.value}')
    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result


def testRequestDownload(channel, config, file_size):
    memory_address_buffer = create_string_buffer(4) 
    memory_size_buffer = create_string_buffer(4)     
    memory_address_size = 4
    memory_size_size = 4
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    print('\n\n*** UDS Service: RequestDownload ***')
    print("Sending initial value 44 (0x44)")
    
    file_size_bytes = file_size.to_bytes(4, byteorder='big')
    for i in range(4):
        memory_size_buffer[i] = file_size_bytes[i]
        
    memory_address_buffer[0] = 0x00
    memory_address_buffer[1] = 0x01
    memory_address_buffer[2] = 0xCC
    memory_address_buffer[3] = 0x00
    
    memory_size_buffer
    print("")
    status = objPCANUds.SvcRequestDownload_2013(channel, config, request, 0x0, 0x0, memory_address_buffer,
                                                memory_address_size, memory_size_buffer,
                                                memory_size_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)
    print('UDS Service: RequestDownload: ' + test_result_to_string(result))
    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result




def testTrasferFile(channel, config, selected_files_result):
    print("Test transfer file",channel, config, selected_files_result)
    file_transfer_thread = threading.Thread(target=testTransferData, args=(channel, config,  selected_files_result))
    file_transfer_thread.start()
    return (True, "File transfer started")




    

################################################## TMP START

def readFileInChunk(offset, chunk_size):
    with open(g_file_path, 'rb') as file:
        file.seek(offset)
        readChukData = file.read(chunk_size)
    return readChukData, len(readChukData)

def testTransferData(channel, config, selected_files_result):
    handle = g_pcan_handle
    config = g_pcan_config
    all_files_data = selected_files_result.get("all_files_data", [])
    sorted_files = sorted(all_files_data, key=lambda x: int(x['sequence_number'], 16))
    for file_data in sorted_files:
        file_path = file_data["file_path"]
        file_size = int(file_data["file_size"], 16)  
        sequence_number = int(file_data["sequence_number"], 16)
        crc32_value = int(file_data["crc16"], 16)
        print(f"\nTransferring file: {file_data['file_name']} (Sequence: {file_data['sequence_number']})")
        print(f"File Path: {file_path}, File Size: {hex(file_size)}")
        is_valid = testRoutineControlCrcCheckCert(handle, config, selected_files_result, sequence_number, crc32_value)
        if not is_valid:
            messagebox.showerror("Routine Error", f"Routine failed for {file_data['file_name']}")
            return response_data, False  
        response_data, is_valid = testRequestDownload(handle, config, file_size)
        if not is_valid:
            messagebox.showerror("Transfer Error", f"Request Download failed for {file_data['file_name']}")
            return response_data, False  
        with open(file_path, "rb") as file:
            buffer = file.read(file_size)  
            chunk_size = 256
            sequence = 0
            file_offset = 0
            index = 0
            status = True
            while index < file_size:
                chunk = buffer[file_offset:file_offset + chunk_size]
                read_bytes = len(chunk)
                result = testTransferDataChunk(channel, config, read_bytes, chunk, sequence)
                transfer_status, _ = result
                if not transfer_status:  
                    print(f"Transfer failed for file chunk at sequence {sequence}")
                    messagebox.showerror("Transfer Error", f"File transfer failed for chunk {sequence} of {file_data['file_name']}")
                    return  
                print(f"Offset: {file_offset}, Read Bytes: {read_bytes}, Sequence: {sequence}")
                file_offset += read_bytes
                sequence += 1
                index += read_bytes
        print(f"File {file_data['file_name']} transfer complete.\n", handle, config, sequence_number)
        response_data, is_valid = testRequestTransferExit(handle, config, sequence_number)
        if not is_valid:
            print("Request Transfer Exit failed")
            messagebox.showerror("Transfer Error", f"Request Transfer Exit failed for {file_data['file_name']}")
            return
        messagebox.showinfo("Transfer status", f"File Downlaod Complete")
    return status




def crc16_ccitt(data: bytes, crc: int = 0xFFFF) -> int:
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # Ensure 16-bit
    return crc


def testTransferDataChunk(channel, config, size, buffer, sequence):
    record = create_string_buffer(size)
    record_size = size
    print("testTransferDataChunk called...")
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()

    for i in range(record_size):
        # time.sleep(10)
        record[i] = buffer[i]
    print("I am here....")
    status = objPCANUds.SvcTransferData_2013(channel, config, request, sequence, record, record_size)
    
    print("channel, config, request, sequence, record, record_size", channel, config, request, sequence, record, record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(f'UDS_SvcTransferData_2013: {status.value}')
    
    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        
        result = display_uds_msg_validate(request, None, False)

    print(f'UDS Service: TransferData: [{sequence}] : {test_result_to_string(result)}')

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    
    return result





################################################## TMP END

def testRequestTransferExit(channel, config, sequence_number):
    record = create_string_buffer(50)  
    record_size = 1  

    request = uds_msg()  
    response = uds_msg()
    confirmation = uds_msg()

    print('\n\n*** UDS Service: RequestTransferExit ***')

    record[0] = sequence_number  

    status = objPCANUds.SvcRequestTransferExit_2013(channel, config, request, record, record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)

    result = False
    response_data = None
    
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        print("*******************", confirmation, response)
        result = display_uds_msg_validate(confirmation, response, False)
        response_data = {
            "request": request,
            "response": response,
            "confirmation": confirmation,
            "type": "Positive" if result else "Negative"
        }
        print("##################", response_data)
    else:
        result = display_uds_msg_validate(request, None, False)
        response_data = {
            "request": request,
            "response": None,
            "confirmation": None,
            "type": "Negative"
        }

    print('UDS Service: RequestTransferExit: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)

    return response_data, result


def testControlDTCSetting(channel, config, controlParameter):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = False

    # Sends a physical ControlDTCSetting message
    print('\n\nSends a physical ControlDTCSetting message: ')
    dtc_setting_control_option_record = (c_uint8 * 1)(0x00)
    status = objPCANUds.SvcControlDTCSetting_2013(channel, config, request, controlParameter,
                                                  dtc_setting_control_option_record, 0)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcControlDTCSetting_2013: %i' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: ControlDTCSetting: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result

def testLinkControl(channel, config):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = False

    print('\n\nSends a physical LinkControl message (Verify Fixed Baudrate): ')
    status = objPCANUds.SvcLinkControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_LC_VBTWFBR,
                                            objPCANUds.PUDS_SVC_PARAM_LC_BAUDRATE_CAN_500K, 0)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcLinkControl_2013: %i' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: LinkControl: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result

def testAccessTimingParameter(channel, config):
    request_record = create_string_buffer(b'\xAB\xCD')
    record_size = c_uint32(2)

    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    request_record[0] = getCChar(0xAB)
    request_record[1] = getCChar(0xCD)

    print('\n\nSends a physical AccessTimingParameter message: ')
    status = objPCANUds.SvcAccessTimingParameter_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_ATP_RCATP,
                                                      request_record, record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcAccessTimingParameter_2013: %d' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: AccessTimingParameter: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result



def testRoutineControlFlashErase(channel, config):
    routine_control_option_record = create_string_buffer(1)
    routine_control_option_record_size = 1

    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    result = False

    print('\n\n*** UDS Service: RoutineControl Erasing Flash***')

    print('\n\nSends a physical RoutineControl message: ')
    for i in range(routine_control_option_record_size):
        routine_control_option_record[i] = 0x0

    status = objPCANUds.SvcRoutineControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_STR, 0x2001,
                                               routine_control_option_record, routine_control_option_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Start: %i' % (status.value))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)

    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()

    status = objPCANUds.SvcRoutineControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_STPR, 0x2001,
                                               routine_control_option_record, routine_control_option_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Stop: %i' % (status.value))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)

    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()

    status = objPCANUds.SvcRoutineControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_RRR, 0x2001,
                                               routine_control_option_record, routine_control_option_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Result: %i' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: RoutineControl Erasing Flash: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result


def testSaveExitRoutine(channel, config, config_type_byte):


    routine_control_option_record = create_string_buffer(2)
    routine_control_option_record_size = 2

    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()
    
    routine_control_option_record_size =1
    for i in range(6):
        routine_control_option_record[0] = config_type_byte
       
    status = objPCANUds.SvcRoutineControl_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_RC_STPR, 0xFD02,
                                                routine_control_option_record, routine_control_option_record_size)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
         status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcRoutineControl_2013 Result: %i' % (status.value))

    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: RoutineControl Erasing Flash: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)

    return result

def testECUReset(channel, config):
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()

    print('\n\n*** UDS Service: ECUReset ***')

    print('\n\nSends a physical ECUReset message: ')
    status = objPCANUds.SvcECUReset_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_ER_HR)
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    print(' UDS_SvcECUReset_2013: %i' % (status.value))
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print('UDS Service: ECUReset: ' + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result


def testTesterPresent(channel, config):
    response_count = c_uint32(0)
    request = uds_msg()
    response = uds_msg()
    confirmation = uds_msg()

    status = objPCANUds.SvcTesterPresent_2013(channel, config, request, objPCANUds.PUDS_SVC_PARAM_TP_ZSUBF)
    print("Execute tester present service: %s" % (test_result_to_string(status)))

    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        status = objPCANUds.WaitForService_2013(channel, request, response, confirmation)
    result = False
    if objPCANUds.StatusIsOk_2013(status, PUDS_STATUS_OK, False):
        result = display_uds_msg_validate(confirmation, response, False)
    else:
        result = display_uds_msg_validate(request, None, False)

    print("UDS Service: TesterPresent: " + test_result_to_string(result))

    status = objPCANUds.MsgFree_2013(request)
    status = objPCANUds.MsgFree_2013(response)
    status = objPCANUds.MsgFree_2013(confirmation)
    return result
########################################### (UDS over CAN: helpers for service tests) ####################################################

def getCChar(c):
    return c if sys.version_info.major >= 3 else chr(c)

def Reverse32(v):
    res = create_string_buffer(4)
    res[3] = getCChar(v & 0x000000FF)
    res[2] = getCChar((v >> 8) & 0x000000FF)
    res[1] = getCChar((v >> 16) & 0x000000FF)
    res[0] = getCChar((v >> 24) & 0x000000FF)
    return res

def display_uds_msg_validate(request, response, no_response_expected):
    
    global g_nbErr
    response_data = {
        "request": None,
        "response": None,
        "type": None
    }

    if request is not None and request.msg.msgdata.isotp:
        print('\nUDS request from 0x%04X (to 0x%04X, with extension address 0x%02X) - result: %i - %s' % (
            request.msg.msgdata.isotp.contents.netaddrinfo.source_addr,
            request.msg.msgdata.isotp.contents.netaddrinfo.target_addr,
            request.msg.msgdata.isotp.contents.netaddrinfo.extension_addr,
            request.msg.msgdata.any.contents.netstatus,
            'ERROR !!!' if request.msg.msgdata.any.contents.netstatus != PCANTP_NETSTATUS_OK.value else 'OK !'))
        request_data = []
        print('\t-> Length: {x1}, Data= '.format(x1=format(request.msg.msgdata.any.contents.length, 'd')), end="") 
        for i in range(request.msg.msgdata.any.contents.length):
            byte = format(request.msg.msgdata.any.contents.data[i], '02X')
            request_data.append(byte)
            print(byte, end=" ")
        print()
        response_data["request"] = request_data

    if response is not None and response.msg.msgdata.isotp:
        print('\nUDS RESPONSE from 0x%04X (to 0x%04X, with extension address 0x%02X) - result: %i - %s' % (
            response.msg.msgdata.isotp.contents.netaddrinfo.source_addr,
            response.msg.msgdata.isotp.contents.netaddrinfo.target_addr,
            response.msg.msgdata.isotp.contents.netaddrinfo.extension_addr,
            response.msg.msgdata.any.contents.netstatus,
            ('ERROR !!!' if response.msg.msgdata.any.contents.netstatus != PCANTP_NETSTATUS_OK.value else 'OK !')))

        response_data_bytes = []
        print('\t-> Length: {x1}, Data= '.format(x1=format(response.msg.msgdata.any.contents.length, 'd')), end="") 
        for i in range(response.msg.msgdata.any.contents.length):
            byte = format(response.msg.msgdata.any.contents.data[i], '02X')
            response_data_bytes.append(byte)
            print(byte, end=" ")
        print()
        response_data["response"] = response_data_bytes

        respSID = request.msg.msgdata.any.contents.data[0] + 0x40
        if respSID == response.msg.msgdata.any.contents.data[0]:
            print('Positive Response')
            response_data["type"] = "Positive"
            return response_data, True
        elif 0x7F == response.msg.msgdata.any.contents.data[0]:
            print('Negative Response')
            response_data["type"] = "Negative"
            g_nbErr += 1
            return response_data, False
        else:
            print('Invalid Response')
            response_data["type"] = "Invalid"
            g_nbErr += 1
            return response_data, False

    elif not no_response_expected:
        print('\n      ERROR: NO UDS RESPONSE !!\n')
        g_nbErr += 1
        response_data["type"] = "No Response"
        return response_data, False

    return response_data, False




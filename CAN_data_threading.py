import html

import can
import time
import binascii
import sys
import os
import requests
import datetime
from datetime import datetime, timezone
from datetime import timedelta
import pytz
import re
# import resources_rc
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from can.interfaces.pcan.basic import PCANBasic, PCAN_USBBUS1, PCAN_ERROR_OK
from openpyxl import Workbook
from openpyxl import load_workbook
from datetime import datetime, timedelta,timezone
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLabel, QHeaderView, QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextBlockFormat
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QTimer
from datetime import datetime, UTC
from A2TDebug import Ui_FinalTestingUtility
import pandas as pd

import serial
import serial.tools.list_ports
import time

# Expected CAN IDs and their frame counts
expected_frame_counts = {0x01: 1, 0x016: 3, 0x013: 3, 0x010: 2, 0x0A: 1, 0x017: 1, 0x018: 1, 0x019: 1, 0x0E: 1, 0x04: 1, 0x05:1, 0x06: 1, 0x07: 1, 0x011: 4, 0x012: 1, 0x01A: 1, 0x01B: 1, 0x03: 1, 0x0B: 1, 0x0C:1, 0x0D:1, 0x0F: 3}

# Initialize received_frames with empty lists for each CAN ID
received_frames = {0x01: [], 0x02: [], 0x03: [], 0x05: [], 0x07: [], 0x016: [], 0x013: [], 0x010: [], 0x0A: [], 0x017: [], 0x018: [], 0x019: [], 0x0E: [], 0x04: [], 0x06: [], 0x011: [], 0x012: [], 0x01A: [], 0x0B: [], 0x0C: [], 0x0D: [], 0x0F:[], 0x21: []}



class mainWindow(QMainWindow):

   
    update_01_singal = pyqtSignal(str,str, str)
    update_03_singal = pyqtSignal(str)
    update_02_singal = pyqtSignal(str,str, str)
    update_05_singal = pyqtSignal(int)
    update_07_signal = pyqtSignal(str, str, str, bool)
    update_08_singal = pyqtSignal(str)
    update_09_singal = pyqtSignal(str)
    update_0A_singal = pyqtSignal(str)
    update_0B_signal = pyqtSignal(str)
    third_frame_signal = pyqtSignal(str)
    update_0C_signal = pyqtSignal(str)
    update_0D_signal = pyqtSignal(str)
    update_0E_signal = pyqtSignal(str)
    update_0F_signal = pyqtSignal(str)
    update_013_singal = pyqtSignal(bool)

    update_016_singal = pyqtSignal(str)
    update_010_signal = pyqtSignal(str)
    update_017_singal = pyqtSignal(str, str, str, str)
    update_018_singal = pyqtSignal(str)
    update_019_singal = pyqtSignal(str)
    update_21_singal = pyqtSignal(str)
    update_04_singal = pyqtSignal(str)
    update_06_signal = pyqtSignal(int, int, int)
    update_011_signal = pyqtSignal(str)
    update_012_signal = pyqtSignal(str, str, str, str)
    update_01A_singal = pyqtSignal(int)
    update_01B_singal = pyqtSignal(int)
    update_015_singal = pyqtSignal(str)
    update_014_singal = pyqtSignal(bool)
    update_retryUI_signal = pyqtSignal(bool,bool)
    
    def __init__(self,can_data=None):
        super().__init__()
        self.message = None
        self.alti = None
        self.long = None
        self.hdop = None
        self.latitude = None
        self.wtdg_cnt = None
        self.wtdg_reboot = None
        self.value = None
        self.CAN_status = None
        self.GSM = None
        self.Time = None
        self.Can_data =can_data
        self.bus =None
        self.busy = False
        self.ui = Ui_FinalTestingUtility()
        self.ui.setupUi(self)
        self.decoded_so_far = None
        self.rearranged_message = None
        self.message = None
        self.ui.setupUi(self)
        self.pcan = PCANBasic()
        self.busy = False
        self.bus = None
        self.IMEI_Str = None
        self.stop_receiving = False
        self.collected_bytes = bytearray()
        self.ui.pushButton.clicked.connect(self.start_functions)
        # self.ui.pushButton_2.clicked.connect(self.save_to_excel)
        # self.ui.pushButton_9.clicked.connect(self.failed_func)
        self.update_01_singal.connect(self.display_0x01)
        self.update_02_singal.connect(self.display_0x02)
        self.update_03_singal.connect(self.display_0x03)
        self.update_05_singal.connect(self.display_0x05)
        self.update_07_signal.connect(self.display_0x07)
        self.update_08_singal.connect(self.display_0x08)
        self.update_09_singal.connect(self.display_0x09)
        self.update_0A_singal.connect(self.display_0x0A)
        self.update_0C_signal.connect(self.display_0x0C)
        self.update_0D_signal.connect(self.display_0x0D)
        self.update_0E_signal.connect(self.display_0x0E)
        self.update_0F_signal.connect(self.display_0x0F)
        self.update_013_singal.connect(self.display_0x013)
        self.update_014_singal.connect(self.display_0x014)
        self.update_016_singal.connect(self.display_0x016)
        self.update_017_singal.connect(self.display_0x017)
        self.update_018_singal.connect(self.display_0x018)
        #self.update_019_singal.connect(self.display_0x019)
        self.third_frame_signal.connect(self.handle_third_frame)
        self.update_04_singal.connect(self.display_0x04)
        self.update_06_signal.connect(self.display_0x06)
        self.update_011_signal.connect(self.display_0x011)
        self.update_012_signal.connect(self.display_0x012)
        self.update_015_singal.connect(self.display_0x015)
        #self.initialize_can_bus()
        self.operator = None
        self.ICCID_string = None
        self.appln_ver = None
        self.BL_ver =None
        self.GSM_ver = None
        self.Gps_ver = None
        self.mains_vtg = None
        self.Gps_status = None
        self.No_of_Sat = None
        self.GPS_fix_time = None
        self.last_pkt_send_tel_epoch = None
        self.last_pkt_send_can_iso = None
        self.CREG = None
        self.CGREG = None
        self.CSQ = None
        self.gprs = None
        self.gsm = None
        self.IMEI_Str = None
        self.ICCID_string = None
        self.operatorName = None
        self.MQTT_status = None
        self.AEPL_MQTT = None
        self.TML_MQTT = None
        self.AEPL_lgn_pkt = None
        self.NOR_Flash_status =None
        self.No_of_LogInPacket =None
        self.time_difference = None
        self.EpochToCurrentTime =None
        self.ActualTime = None
        self.tamper = None
        self.IGN = None
        self.mains_vtg_float = None
        self.readable_time = None
        self.IntVtg_result = None
        self.Gps_result = None
        self.GSM_result = None
        self.DIs_result = None
        self.IGN_result = None
        self.Tamper_result = None
        self.MQTT_result = None
        self.login_pkt_status = None
        self.BL_ver = None
        self.open_cpu_FW_ver = None
        self.open_cpu_SDK_ver = None
        self.IGN = None
        self.MQTT = None
        self.MQTT_server = None
        self.DI1_status = False
        self.DI2_status = False
        self.DI3_status = False
        self.DI1_seen_0 = False
        self.DI1_seen_1 = False
        self.DI2_seen_0 = False
        self.DI2_seen_1 = False
        self.DI3_seen_0 = False
        self.DI3_seen_1 = False
        self.CREG_found = False
        self.CGREG_found = False
        self.CSQ_found = False
        self.operator_found = False
        self.IGN_seen_0 = False
        self.IGN_seen_1 = False
        self.No_of_Sat2 = None
        self.concatenated_hex = None
        self.concatenated_satellites_decimal = None
        self.failFunc_list =[]
        self.Flash_result =None
        self.device_id = None
        self.device_id_found = False
        self.device_id_true = False
        self.erase_status = None
        self.erase_status_found = False
        self.erase_status_true = False
        self.read_status = None
        self.read_status_found = False
        self.read_status_true = False
        self.write_status = None
        self.write_status_found = False
        self.write_status_true = False
        self.watchdog_reboot = None
        self.watchdogreboot_flag = False
        self.watchdog_reboot_count =None
        self.watchdog_reboot_count_dec = None
        self.watchdogrebootCount_flag = False
        self.fun123_checkedin= 0
        self.retry = 0
        self.LED_status = None
        self.CAN_status = None
        self.reboot_str ="Please wait WDT is in progress"
        self.retry_str_flag = "Please wait until retries are done.Starting retries..."
        self.max_retries_flag= False
        self.WDT_MSG_flag = False
        self.GSM_status = None
        self.model = QStandardItemModel()
        self.elapsed_time = 0
        self.timer =QTimer()
        #self.timer.timeout.connect(self.on_timer_timeout)

        self.model.setHorizontalHeaderLabels(['Header', 'Value'])
        # Initialize flags
        self.function100_done = False
        self.function101_done = False
        self.function103_done = False
        self.function104_done = False
        self.function105_done = False
        self.function106_done = False
        self.function115_done = False
        self.function116_done = False
        self.function109_done = False
        self.function110_done = False
        self.function112_done = False
        self.function113_done = False
        self.function114_done = False
        self.function102_done = False
        self.function119_done = False
        self.function108_done = False
        # Timer for delays
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)  # Ensure it only fires once
        self.timer.timeout.connect(self.execute_next_function)
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_time)
        self.timer1.start(1000)  # Update every second
        self.timer2 = QTimer(self)
        self.ui.pushButton_3.clicked.connect(self.fun_0x014_LED_ON)
        self.ui.pushButton_4.clicked.connect(self.fun_0x014_LED_OFF)

        self.ui.pushButton_6.clicked.connect(self.fun_0x013_CAN_OFF)
        self.ui.pushButton.clicked.connect(self.start_functions)
        #self.ui.pushButton.clicked.connect(self.start_functions)
        self.ui.pushButton_2.clicked.connect(self.save_to_excel)

        self.update_time()
        self.timer = QTimer()

        # Automatically detect port
        self.relay_port = self.find_relay_port()

        if not self.relay_port:
            print("USB Relay module not found!")
            exit(1)

        print(f"Found relay module at {self.relay_port}")

        # def initialize_can_bus(self):
    #     try:
    #         # Initialize the bus once, not inside each function
    #         self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=250000)
    #         #print(f"CAN Bus initialized: {self.bus.channel_info}")
    #     except can.CanError as e:
    #         print(f"Error initializing CAN bus: {str(e)}")
    #         self.bus = None  # Set bus to None if there's an initialization error

        #self.start_functions()


    def start_functions(self):



            try:

                 #while(1):
                 self.fun_0x01()
                 QApplication.processEvents()
                 self.fun_0x02()
                 QApplication.processEvents()
                 self.fun_0x03()
                 QApplication.processEvents()
                 self.fun_0x04()
                 QApplication.processEvents()
                 self.fun_0x05()
                 QApplication.processEvents()
                 self.fun_0x06()
                 QApplication.processEvents()
                 self.fun_0x07()
                 QApplication.processEvents()
                 self.fun_0x08()
                 QApplication.processEvents()
                 self.fun_0x09()
                 QApplication.processEvents()
                 self.fun_0x0A()
                 QApplication.processEvents()
                 self.fun_0x0B()
                 QApplication.processEvents()
                 self.fun_0x0C()
                 QApplication.processEvents()
                 self.fun_0x0D()
                 QApplication.processEvents()
                 self.fun_0x0E()
                 QApplication.processEvents()
                 self.fun_0x0F()
                 QApplication.processEvents()
                 self.fun_0x011()
                 QApplication.processEvents()
                 self.fun_0x012()
                 QApplication.processEvents()
                 self.fun_0x015()
                 QApplication.processEvents()

            finally:
                self.busy = False


    def start_timer(self):
        self.timer.timeout.connect(self.start_functions)
        self.timer.start(1000)  # every 1000 ms (1 second)

    def start_thread(self):
        # Start the update method in a separate thread
        thread = threading.Thread(target=self.start_functions)
        thread.daemon = True  # This will allow the thread to exit when the program exits
        thread.start()

    # def on_timer_timeout(self):
    #     self.elapsed_time += 1
    #     self.ui.operator_Input_3.setPlainText(f"{self.elapsed_time} Sec")
    #     self.ui.operator_Input_3.setStyleSheet("""
    #         font-size: 16px;
    #         background-color: white;
    #     """)
    #     self.ui.operator_Input_3.setAlignment(Qt.AlignCenter)
    #     print("elapsed time", self.elapsed_time)

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd\n HH:mm:ss")
        self.ui.operator_Input_2.setPlainText(current_time)


        
    def fun_0x016(self,retry_mode =False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return
            
        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x016, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)
            
            for i in range(expected_frame_counts[0x016]):
                message = self.bus.recv(timeout=2)  
                
                if message:
                    received_frames[0x016].append(message)
                    
                else:
                    print(f"Timeout waiting for message for CAN ID 0x100. No response received.")
 
            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x016]) == expected_frame_counts[0x016]:
                frames = received_frames[0x016]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x016: {complete_message.hex()}")
 
                ICCID = complete_message[:20]
                print(f"Extracted ICCID: {ICCID}")

                try:
                    if ICCID:
                        self.ICCID_string = ICCID.decode('ascii')
                        print("ICCID Str:", self.ICCID_string)
                        self.update_016_singal.emit(str(self.ICCID_string))

                        # Create the model with two columns

                except UnicodeDecodeError:
                  print("Error decoding ICCID to Hex. The data may contain non-ASCII characters.")
 
            else:
                print(f"Not all frames received for CAN ID 0x016. Expected {expected_frame_counts[0x016]}, but received {len(received_frames[0x016])}.")
 
        except can.CanError as e:
            print(f"CAN error: {str(e)}")
 
        finally:
            self.busy = False  # Mark the system as not busy
            #self.function101_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x016].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()
    def display_0x016(self):
        self.ui.plainTextEdit_2.setPlainText(self.ICCID_string)

        self.ui.textEdit.append(f"ICCID: {str(self.ICCID_string)}")

    def fun_0x017(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x017, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)

            for i in range(expected_frame_counts[0x017]):
                message = self.bus.recv(timeout=2)

                if message:
                    received_frames[0x017].append(message)

                else:
                    print(f"Timeout waiting for message for CAN ID 0x100. No response received.")

            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x017]) == expected_frame_counts[0x017]:
                frames = received_frames[0x017]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x016: {complete_message.hex()}")

                try:
                    complete_message = complete_message.hex()
                    self.device_ID = complete_message[0]
                    print("Device ID", self.device_ID)
                    self.erase_status = complete_message[1]
                    print("Erase Status", self.erase_status)
                    self.read_status = complete_message[2]
                    print("Read Status", self.read_status)
                    self.write_status = complete_message[3]
                    print("Write Status", self.write_status)

                    self.update_017_singal.emit(str(self.device_ID), str(self.erase_status), str(self.read_status), str(self.write_status))
                except UnicodeDecodeError:
                    print("Error decoding NOR Flash Status to Hex. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x017. Expected {expected_frame_counts[0x017]}, but received {len(received_frames[0x017])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function101_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x016].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()

    def display_0x017(self):

        self.ui.textEdit.append(
            f"Device ID: {str(self.device_ID)}\nErase Status: {str(self.erase_status)}\nRead Status: {str(self.read_status)}\nWrite Status: {str(self.write_status)}")
        self.ui.plainTextEdit_20.setPlainText(str(self.device_ID))

    def fun_0x018(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x018, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)

            for i in range(expected_frame_counts[0x018]):
                message = self.bus.recv(timeout=2)

                if message:
                    received_frames[0x018].append(message)

                else:
                    print(f"Timeout waiting for message for CAN ID 0x100. No response received.")

            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x018]) == expected_frame_counts[0x018]:
                frames = received_frames[0x018]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x016: {complete_message.hex()}")

                try:
                    complete_message = complete_message.hex()
                    print("Watchdog Reboot", str(complete_message[0]))
                    self.wtdg_reboot = str(complete_message[0])
                    self.update_018_singal.emit(str(self.wtdg_reboot))
                except UnicodeDecodeError:
                    print("Error decoding watchdog reboot status")

            else:
                print(
                    f"Not all frames received for CAN ID 0x018. Expected {expected_frame_counts[0x018]}, but received {len(received_frames[0x018])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function101_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x016].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()

    def display_0x018(self):
        #self.ui.plainTextEdit_22.setPlainText(str(self.wtdg_reboot))
        self.ui.textEdit.append(f"Watchdog Reboot: {str(self.wtdg_reboot)}")


    def fun_0x03(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Initialize CAN bus if not already
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark system as busy

        try:
            msg = can.Message(arbitration_id=0x03, data=[0] * 8, is_extended_id=False)
            print("Sending message to 0x03:", msg)
            self.bus.send(msg)

            # Receive expected frames
            for _ in range(expected_frame_counts[0x03]):
                message = self.bus.recv(timeout=2)
                if message:
                    received_frames[0x03].append(message)
                else:
                    print("Timeout waiting for message for CAN ID 0x03.")

            # Process received frames
            if len(received_frames[0x03]) == expected_frame_counts[0x03]:
                frames = received_frames[0x03]
                frames.sort(key=lambda x: x.data[0])  # Sort by first byte
                complete_message = b''.join(frame.data for frame in frames)
                print("Complete message:", complete_message)

                # Decode latitude
                self.latitude = self.decode_signal(complete_message, 8, 32)
                if self.latitude:
                    self.latitude = self.latitude[0] * 10_000_000
                    formatted_latitude = f"{self.latitude:.7f}"  # Format to 7 decimal places
                    print("Latitude:", formatted_latitude)

                    self.update_03_singal.emit(formatted_latitude)
                else:
                    print("Latitude decoding returned None.")

            else:
                print(f"Not all frames received for CAN ID 0x03. "
                      f"Expected {expected_frame_counts[0x03]}, "
                      f"but received {len(received_frames[0x03])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Reset busy flag
            if self.bus:
                self.bus.shutdown()
                self.bus = None
            received_frames[0x03].clear()

            if not retry_mode:
                self.execute_next_function()

    def display_0x03(self):
        self.ui.plainTextEdit_23.setPlainText(str(self.latitude))

        self.ui.textEdit.append(f"Latiude: {str(self.latitude)}")


    def fun_0x04(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x04, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)

            # Wait for the response
            for i in range(expected_frame_counts[0x04]):
                message = self.bus.recv(timeout=2)  # 2 second timeout for each frame
                if message:
                    received_frames[0x04].append(message)

                else:
                    print(f"Timeout waiting for message for CAN ID 0x04. No response received.")

            # Check if we have received all expected frames for 0x013
            if len(received_frames[0x04]) == expected_frame_counts[0x04]:
                frames = received_frames[0x04]
                frames.sort(key=lambda x: x.data[0])
                complete_message = b''.join(frame.data[0:] for frame in frames)

                long = complete_message[6:12]
                complete_message = b''.join(frame.data[0:] for frame in frames)
                print("complete_message", complete_message)
                long = self.decode_signal(complete_message, 8, 32)


                print("Long", long)
                #print("Alti", alti)
                try:
                    if long:
                        # self.latitude = latitude.decode('ascii')

                        self.long = long[0]*10_000_000
                        self.update_04_singal.emit(str(self.long))
                        print("longitude:", self.long)
                        # Create the model with two columns

                except UnicodeDecodeError:
                    print("Error decoding latitude to ASCII. The data may contain non-ASCII characters.")
            else:
                print(
                    f"Not all frames received for CAN ID 0x04. Expected {expected_frame_counts[0x04]}, but received {len(received_frames[0x04])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            #self.function013_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x04].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()

    def display_0x04(self):
        self.ui.plainTextEdit_25.setPlainText(str(self.long))

        self.ui.textEdit.append(f"Longitude: {self.long}")



    def fun_0x06(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x06, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)

            # Wait for the response
            for i in range(expected_frame_counts[0x06]):
                message = self.bus.recv(timeout=2)  # 2 second timeout for each frame
                if message:
                    received_frames[0x06].append(message)

                else:
                    print(f"Timeout waiting for message for CAN ID 0x04. No response received.")

            # Check if we have received all expected frames for 0x013
            if len(received_frames[0x06]) == expected_frame_counts[0x06]:
                frames = received_frames[0x06]
                frames.sort(key=lambda x: x.data[0])
                complete_message = b''.join(frame.data[0:] for frame in frames)
                print("complete_message", complete_message)
                hdop = self.decode_signal(complete_message, 41, 8)
                pdop = self.decode_signal(complete_message, 50, 8)
                cource = self.decode_signal(complete_message, 8, 32)
                # alti = complete_message[16:]
                print("PDOP msg", pdop)
                print("HDOP", hdop)
                print("cource", cource)
                # print("Alti", alti)
                try:
                    if hdop and pdop and cource:
                        self.hdop = hdop[0]
                        print("HDOP:", self.hdop)
                        self.pdop = pdop[0]
                        print("PDOP", self.pdop)
                        self.cource = cource[0]
                        print("cource", self.cource)
                        self.update_06_signal.emit(self.hdop, self.pdop, self.cource)

                        # Create the model with two columns

                except UnicodeDecodeError:
                    print("Error decoding latitude to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x04. Expected {expected_frame_counts[0x04]}, but received {len(received_frames[0x04])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            #self.function013_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x06].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()

    def display_0x06(self):
        self.ui.plainTextEdit_26.setPlainText(str(self.hdop))
        self.ui.plainTextEdit_27.setPlainText(str(self.pdop))
        self.ui.plainTextEdit_15.setPlainText(str(self.cource))

        self.ui.textEdit.append(f"HDOP: {self.hdop}, PDOP: {self.pdop}, COURCE: {self.cource}")

    def fun_0x07(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x07, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)

            # Wait for the response
            for i in range(expected_frame_counts[0x07]):
                message = self.bus.recv(timeout=2)  # 2 second timeout for each frame

                if message:
                    print("0x07 msg", message)
                    received_frames[0x07].append(message)

                else:
                    print(f"Timeout waiting for message for CAN ID 0x07. No response received.")
            print("received frames", (received_frames))
            # Check if we have received all expected frames for 0x013
            if len(received_frames[0x07]) == expected_frame_counts[0x07]:
                frames = received_frames[0x07]
                frames.sort(key=lambda x: x.data[0])
                complete_message = b''.join(frame.data[0:] for frame in frames)
                print("complete_message", complete_message)
                CSQ = self.decode_signal(complete_message, 25, 8)
                GPRS = self.decode_signal(complete_message, 34, 8)
                GSM = self.decode_signal(complete_message, 35, 8)
                print("Operator", complete_message)
                print("CSQ",CSQ)
                self.operatorName = complete_message[1:3].decode('ascii').rstrip("\0")
                try:
                    if CSQ or GPRS or GSM or self.operatorName:
                        self.CSQ = CSQ[0]
                        print("CSQ:", self.CSQ)
                        self.gprs = bool(GPRS[0])
                        print("GPRS", self.gprs)
                        self.GSM_status = bool(GSM[0])
                        print("GSM", self.GSM_status)
                        print("Operator",self.operatorName)
                        self.update_07_signal.emit(str(self.operatorName),str(self.CSQ), str(self.gprs), self.GSM_status )

                        # Create the model with two columns

                except UnicodeDecodeError:
                    print("Error decoding latitude to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x07. Expected {expected_frame_counts[0x07]}, but received {len(received_frames[0x07])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            #self.function013_done = True`
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x07].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()


    def display_0x07(self):
        self.ui.plainTextEdit_18.setPlainText(str(self.CSQ))
        self.ui.plainTextEdit_7.setPlainText(str(self.operatorName))
        self.ui.plainTextEdit_4.setPlainText(str(self.GSM_status))
        self.ui.plainTextEdit_5.setPlainText(str(self.gprs))

        self.ui.textEdit.append(f"CSQ: {self.CSQ}\nOperator: {self.operatorName}\nGSM:{self.GSM_status}\nGPRS:{self.gprs}")\

    def fun_0x012(self, retry_mode=False):
        print("0x012 Called...")
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x012, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)

            # Wait for the response
            for i in range(expected_frame_counts[0x012]):
                message = self.bus.recv(timeout=2)  # 2 second timeout for each frame
                if message:
                    received_frames[0x012].append(message)
                    print("MQTT", message)
                else:
                    print(f"Timeout waiting for message for CAN ID 0x04. No response received.")

            # Check if we have received all expected frames for 0x013
            if len(received_frames[0x012]) == expected_frame_counts[0x012]:
                frames = received_frames[0x012]
                frames.sort(key=lambda x: x.data[0])
                complete_message = b''.join(frame.data[0:] for frame in frames)
                print("complete_message", complete_message)
                AEPL_MQTT = self.decode_signal(complete_message, 8, 1)
                TML_MQTT = self.decode_signal(complete_message, 9, 1)
                AEPL_lgn_pkt = self.decode_signal(complete_message, 10, 1)
                NOR_Flash_status = self.decode_signal(complete_message, 11, 1)

                try:
                    if AEPL_MQTT and TML_MQTT and AEPL_lgn_pkt and NOR_Flash_status:
                        self.AEPL_MQTT = bool(AEPL_MQTT)
                        print("AEPL_MQTT:", self.AEPL_MQTT)
                        self.TML_MQTT = bool(TML_MQTT)
                        print("TML_MQTT", self.TML_MQTT)
                        self.AEPL_lgn_pkt = bool(AEPL_lgn_pkt)
                        print("AEPL_lgn_pkt", self.AEPL_lgn_pkt)
                        self.NOR_Flash_status = bool(NOR_Flash_status)
                        print("NOR_Flash_status", self.NOR_Flash_status)
                        self.update_012_signal.emit(str(self.AEPL_MQTT),str(self.TML_MQTT), str(self.AEPL_lgn_pkt), str(self.NOR_Flash_status))

                        # Create the model with two columns

                except UnicodeDecodeError:
                    print("Error decoding latitude to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x012. Expected {expected_frame_counts[0x012]}, but received {len(received_frames[0x012])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busyNOR_Flash_status
            #self.function013_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x012].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()

    def display_0x012(self):
        self.ui.plainTextEdit_34.setPlainText(str(self.AEPL_MQTT))
        self.ui.plainTextEdit_6.setPlainText(str(self.TML_MQTT))
        self.ui.plainTextEdit_35.setPlainText(str(self.AEPL_lgn_pkt))
        self.ui.plainTextEdit_20.setPlainText(str(self.NOR_Flash_status))

        self.ui.textEdit.append(f"AEPL MQTT: {self.AEPL_MQTT}\nTML MQTT: {self.TML_MQTT}\nAEPL login pkt:{self.AEPL_lgn_pkt}\nNOR Flash status:{self.NOR_Flash_status}")



    def fun_0x0B(self):
        if self.busy:
            print("System is busy, please wait...")
            return

        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True

        try:
            # Send request message to arbitration ID 0x0B
            msg = can.Message(arbitration_id=0x0B, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)
            print("Request message sent to CAN ID 0x0B.")

            # Wait for a single response
            message = self.bus.recv(timeout=2)
            if message:
                print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")

                try:
                    payload = message.data[1:]
                    decoded_text = payload.decode('ascii', errors='ignore').rstrip("\0")
                    self.appln_ver = decoded_text

                    # Emit signal with received version
                    self.third_frame_signal.emit(decoded_text)
                    print(f"Application version (decoded): {decoded_text}")
                except Exception as e:
                    print(f"Error decoding frame data: {str(e)}")
            else:
                print("Timeout waiting for response from CAN ID 0x0B.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False
            if self.bus:
                self.bus.shutdown()
                self.bus = None

    def handle_third_frame(self, frame_text):
        print(f"3rd frame data received and decoded: {frame_text}")
        self.ui.plainTextEdit_37.setPlainText(str(self.appln_ver))
        self.ui.textEdit.append(f"Application FW Version: {str(self.appln_ver)}")

    def fun_0x0C(self):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x0C, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for the response
            for i in range(expected_frame_counts[0x0C]):
                message = self.bus.recv(timeout=2)  # 1 second timeout for each frame
                if message:
                    print("Bootloader Version", message)
                    print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                    received_frames[0x0C].append(message)
                else:
                    print(f"Timeout waiting for message for CAN ID 0x104. No response received.")

            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x0C]) == expected_frame_counts[0x0C]:
                frames = received_frames[0x0C]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x100: {complete_message.hex()}")

                try:
                    self.BL_ver = complete_message.decode('ascii').rstrip("\0")  # Convert all bytes to hex string
                    # self.BL_ver = complete_message.hex()
                    self.update_0C_signal.emit(str(self.BL_ver))
                    print(f"Bootloader version (raw hex): {self.BL_ver}")

                # self.update_104_singal.emit(self.BL_ver)
                # self.ui.textEdit.append(f"Bootloader version:{hex(self.BL_ver)}")
                except UnicodeDecodeError:
                    print("Error decoding BL Version to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x0C. Expected {expected_frame_counts[0x0C]}, but received {len(received_frames[0x0C])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function104_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x0C].clear()
            # if not retry_mode:  # Skip calling execute_next_function during retries
            #     self.execute_next_function()

    def display_0x0C(self):
        self.ui.plainTextEdit_8.setPlainText(str(self.BL_ver))

        self.ui.textEdit.append(f"Bootloader Version:{str(self.BL_ver)}")

    def fun_0x0D(self):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x0D, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for the response
            for i in range(expected_frame_counts[0x0D]):
                message = self.bus.recv(timeout=2)  # 1 second timeout for each frame
                if message:
                    print("Open Cpu SDK version", message)
                    print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                    received_frames[0x0D].append(message)
                else:
                    print(f"Timeout waiting for message for CAN ID 0x0D. No response received.")

            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x0D]) == expected_frame_counts[0x0D]:
                frames = received_frames[0x0D]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x0D: {complete_message.hex()}")

                try:
                    self.open_cpu_FW_ver = complete_message.decode('ascii').rstrip("\0")  # Convert all bytes to hex string
                    # self.BL_ver = complete_message.hex()
                    self.update_0D_signal.emit(str(self.open_cpu_FW_ver))
                    print(f"Open Cpu SDK version (raw hex): {self.open_cpu_FW_ver}")

                # self.update_104_singal.emit(self.BL_ver)
                # self.ui.textEdit.append(f"Bootloader version:{hex(self.BL_ver)}")
                except UnicodeDecodeError:
                    print("Error decoding SDK Version to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x0D. Expected {expected_frame_counts[0x0D]}, but received {len(received_frames[0x0D])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function104_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x0D].clear()
            # if not retry_mode:  # Skip calling execute_next_function during retries
            #     self.execute_next_function()

    def display_0x0D(self):
        self.ui.plainTextEdit_9.setPlainText(str(self.open_cpu_FW_ver))

        self.ui.textEdit.append(f"Open Cpu SDK version:{str(self.open_cpu_FW_ver)}")


    def fun_0x0E(self):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x0E, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for the response
            for i in range(expected_frame_counts[0x0E]):
                message = self.bus.recv(timeout=2)  # 1 second timeout for each frame
                if message:
                    print("Open Cpu SDK version", message)
                    print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                    received_frames[0x0E].append(message)
                else:
                    print(f"Timeout waiting for message for CAN ID 0x0D. No response received.")

            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x0E]) == expected_frame_counts[0x0E]:
                frames = received_frames[0x0E]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x0E: {complete_message.hex()}")

                try:
                    self.open_cpu_SDK_ver = complete_message.decode('ascii').rstrip("\0")  # Convert all bytes to hex string
                    # self.BL_ver = complete_message.hex()
                    self.update_0E_signal.emit(str(self.open_cpu_SDK_ver))
                    print(f"Open Cpu SDK version (raw hex): {self.open_cpu_SDK_ver}")

                # self.update_104_singal.emit(self.BL_ver)
                # self.ui.textEdit.append(f"Bootloader version:{hex(self.BL_ver)}")
                except UnicodeDecodeError:
                    print("Error decoding SDK Version to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x0E. Expected {expected_frame_counts[0x0E]}, but received {len(received_frames[0x0E])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function104_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x0E].clear()
            # if not retry_mode:  # Skip calling execute_next_function during retries
            #     self.execute_next_function()

    def display_0x0E(self):
        self.ui.plainTextEdit_38.setPlainText(str(self.open_cpu_SDK_ver))

        self.ui.textEdit.append(f"Open Cpu SDK version:{str(self.open_cpu_SDK_ver)}")

    def fun_0x0F(self):
        if self.busy:
            print("System is busy, please wait...")
            return

        self.busy = True
        received_frames[0x0F].clear()  # Clear old data

        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                self.busy = False
                return

        try:
            # Send request message
            msg = can.Message(arbitration_id=0x0F, data=[0] * 8, is_extended_id=False)
            self.bus.send(msg)

            # Receive frames
            for i in range(expected_frame_counts[0x0F]):
                message = self.bus.recv(timeout=3)
                if message:
                    print(f"Frame seq: {message.data[0]}, Data: {message.data[1:].hex()}")
                    received_frames[0x0F].append(message)
                else:
                    print("Timeout waiting for message for CAN ID 0x0F.")

            if len(received_frames[0x0F]) == expected_frame_counts[0x0F]:
                frames = received_frames[0x0F]
                frames.sort(key=lambda x: x.data[0])
                complete_message = b''.join(frame.data[1:] for frame in frames)

                try:
                    imei_str = complete_message.decode('ascii').strip()
                    print(f"Decoded IMEI: {imei_str}")
                    self.IMEI_Str = imei_str
                    self.update_0F_signal.emit(self.IMEI_Str)
                except UnicodeDecodeError:
                    print("Error decoding IMEI to ASCII.")
            else:
                print(f"Incomplete frame set: expected {expected_frame_counts[0x0F]}, got {len(received_frames[0x0F])}")
                # Do NOT emit signal — UI will not be updated

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False

    def display_0x0F(self, imei_str):
        print(f"display_0x0F called with IMEI: {imei_str}")
        self.ui.plainTextEdit.setPlainText(imei_str)
        self.ui.textEdit.append(f"IMEI: {imei_str}")

    def fun_0x011(self):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x011, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for the response
            for i in range(expected_frame_counts[0x011]):
                message = self.bus.recv(timeout=2)  # 1 second timeout for each frame
                if message:
                    print("ICCID", message)
                    print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                    received_frames[0x011].append(message)
                else:
                    print(f"Timeout waiting for message for CAN ID 0x011. No response received.")

            # Check if we have received all expected frames for 0x100
            if len(received_frames[0x011]) == expected_frame_counts[0x011]:
                frames = received_frames[0x011]
                frames.sort(key=lambda x: x.data[0])  # Sort by sequence number
                complete_message = b''.join(frame.data[1:] for frame in frames)
                print(f"Reassembled message for CAN ID 0x0F: {complete_message.hex()}")

                try:
                    self.ICCID_string = complete_message.decode('ascii').rstrip("\0")  # Convert all bytes to hex string
                    # self.BL_ver = complete_message.hex()
                    self.update_011_signal.emit(str(self.ICCID_string))
                    print(f"ICCID: {self.ICCID_string}")

                # self.update_104_singal.emit(self.BL_ver)
                # self.ui.textEdit.append(f"Bootloader version:{hex(self.BL_ver)}")
                except UnicodeDecodeError:
                    print("Error decoding ICCID to ASCII. The data may contain non-ASCII characters.")

            else:
                print(
                    f"Not all frames received for CAN ID 0x011. Expected {expected_frame_counts[0x011]}, but received {len(received_frames[0x011])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function104_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x011].clear()
            # if not retry_mode:  # Skip calling execute_next_function during retries
            #     self.execute_next_function()

    def display_0x011(self):
        self.ui.plainTextEdit_2.setPlainText(str(self.ICCID_string))

        self.ui.textEdit.append(f"ICCID: {str(self.ICCID_string)}")


    def fun_0x02(self, retry_mode=False):
        print('0x02 called')

        if self.busy:
            print("System is busy, please wait...")
            return

        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True

        try:
            # Send request message
            msg = can.Message(arbitration_id=0x02, data=[0] * 8, is_extended_id=False)
            self.bus.send(msg)

            # Receive response
            message = self.bus.recv(timeout=2)
            print("Received message:", message)

            if message:
                data_bytes = list(message.data)
                print("Raw data bytes:", data_bytes)

                # Decode GPS Status (1 bit at bit 8)
                gps_status_bits = self.decode_signal(message.data, 8, 1)
                self.Gps_status = gps_status_bits[0] if gps_status_bits else None
                print('Gps status:', self.Gps_status)

                # Decode Number of Satellites (8 bits at bit 42)
                sat_bits = self.decode_signal(message.data, 42, 8)
                self.No_of_Sat = sat_bits[0] if sat_bits else None
                print('Number of satellites:', self.No_of_Sat)

                # Decode GPS Fix Time (32 bits at bit 9)
                gps_time_bits = self.decode_signal(message.data, 9, 32)
                self.GPS_fix_time = gps_time_bits[0] if gps_time_bits else None
                print('GPS Fix Time:', self.GPS_fix_time)

                # Convert to datetime
                if self.GPS_fix_time:
                    self.ActualTime = datetime.fromtimestamp(self.GPS_fix_time, timezone.utc)
                    print("Actual time:", self.ActualTime)
                else:
                    self.ActualTime = "Invalid"
                    print("Invalid GPS fix time")

                # Optionally store satellite history
                if not hasattr(self, 'satellite_history'):
                    self.satellite_history = []
                self.satellite_history.append(self.No_of_Sat)

                # Emit signal
                self.update_02_singal.emit(
                    str(self.Gps_status),
                    str(self.No_of_Sat),
                    str(self.No_of_Sat)
                )

            else:
                print("Timeout waiting for response to CAN ID 0x02.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False
            self.function109_done = True

            if self.bus:
                self.bus.shutdown()
                self.bus = None

            received_frames[0x02].clear()

            if not retry_mode:
                self.execute_next_function()

    def display_0x02(self):
        self.ui.plainTextEdit_5.setPlainText(str(self.Gps_status))
        self.ui.plainTextEdit_11.setPlainText(str(self.No_of_Sat))  # Shows satellite count
        self.ui.plainTextEdit_14.setPlainText(str(self.ActualTime))

        self.ui.textEdit.append(
            f"Gps Status: {self.Gps_status}\n"
            f"No. of Satellites: {self.No_of_Sat}\n"
            f"Actual Time: {self.ActualTime}"
        )

    def fun_0x08(self,retry_mode = False):
        print('inside 0x08')
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return
            
        self.busy = True  # Mark the system as busy

        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x08, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)
            #print(f"Message sent on {self.bus.channel_info}")

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv(timeout=2)  # 2 seconds timeout for response

            if message:
                #print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                self.last_pkt_send_tel_epoch = self.decode_signal(message.data, 8, 32)
                print('last_pkt_send_tel_epoch :', self.last_pkt_send_tel_epoch)
                # self.GPS_fix_time = self.decode_signal(message.data, 9, 32)
                # self.GPS_fix_time = self.GPS_fix_time[0]
                # print('GPS_fix_time', str(self.GPS_fix_time))

                if self.last_pkt_send_tel_epoch:
                    value = self.last_pkt_send_tel_epoch
                    self.ActualTime = datetime.fromtimestamp(value[0], timezone.utc)
                    print("Actual time", self.ActualTime)
                else:
                    print("Unexpected GPS_fix_time length:", len(self.GPS_fix_time))

                self.update_08_singal.emit(str(self.ActualTime))

            else:
                # If no message is received within the timeout period
                print(f"Timeout waiting for message for CAN ID 0x08. No response received.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")
 
        finally:
            self.busy = False  # Mark the system as not busy
    def display_0x08(self):
        self.ui.plainTextEdit_31.setPlainText("NA")
        self.ui.plainTextEdit_31.setEnabled(False)
        self.ui.textEdit.append(f"Telemetry Last pkt: {str(self.ActualTime)}\n")
        self.ui.label_32.setEnabled(False)
        self.ui.label_34.setEnabled(False)

    def fun_0x09(self, retry_mode=False):
        print('inside 0x09')
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x09, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv(timeout=2)  # 2 seconds timeout for response

            if message:
                # print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                self.last_pkt_send_can_iso = self.decode_signal(message.data, 8, 32)
                print('last_pkt_send_can_iso :', self.last_pkt_send_can_iso)
                # self.GPS_fix_time = self.decode_signal(message.data, 9, 32)
                # self.GPS_fix_time = self.GPS_fix_time[0]
                # print('GPS_fix_time', str(self.GPS_fix_time))

                if self.last_pkt_send_can_iso:
                    value = self.last_pkt_send_can_iso
                    self.ActualTime = datetime.fromtimestamp(value[0], timezone.utc)
                    print("Actual time", self.ActualTime)
                else:
                    print("Unexpected last_pkt_send_can_iso length:", len(self.GPS_fix_time))

                self.update_09_singal.emit(str(self.ActualTime))

            else:
                # If no message is received within the timeout period
                print(f"Timeout waiting for message for CAN ID 0x08. No response received.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy

    def display_0x09(self):
        self.ui.plainTextEdit_32.setPlainText("NA")
        self.ui.plainTextEdit_32.setEnabled(False)
        self.ui.label_33.setEnabled(False)
        self.ui.textEdit.append(f"CAN ISO Last pkt: {str(self.ActualTime)}\n")

    def fun_0x0A(self, retry_mode=False):
        print('inside 0x0A')
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x0A, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv(timeout=2)  # 2 seconds timeout for response

            if message:
                # print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                self.last_immo_cmd_epoch = self.decode_signal(message.data, 8, 32)
                print('last_immo_cmd_epoch :', self.last_immo_cmd_epoch)
                # self.GPS_fix_time = self.decode_signal(message.data, 9, 32)
                # self.GPS_fix_time = self.GPS_fix_time[0]
                # print('GPS_fix_time', str(self.GPS_fix_time))

                if self.last_immo_cmd_epoch:
                    value = self.last_immo_cmd_epoch
                    self.ActualTime = datetime.fromtimestamp(value[0], timezone.utc)
                    print("Actual time", self.ActualTime)
                else:
                    print("Unexpected last_pkt_send_can_iso length:", len(self.last_immo_cmd_epoch))

                self.update_0A_singal.emit(str(self.ActualTime))

            else:
                # If no message is received within the timeout period
                print(f"Timeout waiting for message for CAN ID 0x08. No response received.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy


    def display_0x0A(self):
        self.ui.plainTextEdit_21.setPlainText("NA")
        self.ui.plainTextEdit_21.setEnabled(False)
        self.ui.textEdit.append(f"last pkt send can iso: {self.ActualTime}")
        self.ui.label_23.setEnabled(False)
        self.ui.label_14.setEnabled(False)




    def fun_0x013_CAN_OFF(self, retry_mode=False):
        print('inside 0x015')
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x013, data=[0, 1, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)
            # print(f"Message sent on {self.bus.channel_info}")

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv()  # 2 seconds timeout for response

            if message:
                # print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                self.CAN_status = self.decode_signal(message.data, 8, 1)
                self.CAN_status = self.CAN_status[1]
                print('CAN_Status :', self.CAN_status)
                if self.CAN_status == 0:
                    self.CAN_status = True

                # self.GPS_fix_time = self.decode_signal(message.data, 9, 32)
                # self.GPS_fix_time = self.GPS_fix_time[0]
                # print('GPS_fix_time', str(self.GPS_fix_time))


                self.update_013_singal.emit(bool(self.CAN_status))
                if message == '00000000':
                    self.showpopup("Please Restart the device")

            else:
                # If no message is received within the timeout period
                print(f"Timeout waiting for message for CAN ID 0x08. No response received.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy


    def fun_0x013(self, retry_mode=False):
        print('inside 0x013')
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x013, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)
            print(f"Message sent on {self.bus.channel_info}{msg}")

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv(timeout=2.0)  # 2 seconds timeout for response

            if message:
                # print(f"Received message from CAN ID {hex(message.arbitration_id)}: {message.data.hex()}")
                self.CAN_status = self.decode_signal(message.data, 8, 1)
                self.CAN_status = self.CAN_status[1]
                print("CAN On Status", self.CAN_status)

                if self.CAN_status == 1:
                    self.CAN_status = True
                print('CAN_Status :', self.CAN_status)
                # self.GPS_fix_time = self.decode_signal(message.data, 9, 32)
                # self.GPS_fix_time = self.GPS_fix_time[0]
                # print('GPS_fix_time', str(self.GPS_fix_time))


                self.update_013_singal.emit(str(self.CAN_status))

            else:
                # If no message is received within the timeout period
                print(f"Timeout waiting for message for CAN ID 0x08. No response received.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy

    def display_0x013(self):
        self.ui.plainTextEdit_19.setPlainText(str(self.CAN_status))

        self.ui.textEdit.append(f"CAN status: {str(self.CAN_status)}")

    def fun_0x014_LED_OFF(self, retry_mode=False):
        print('[INFO] Inside 0x014 LED OFF function')
        if self.busy:
            print("[WARN] System is busy, please wait...")
            return

        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("[INFO] PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"[ERROR] CAN bus init failed: {str(e)}")
                return

        self.busy = True

        try:
            # LED OFF command
            msg = can.Message(arbitration_id=0x014, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)
            print("[INFO] Sent LED OFF message:", msg.data)

            response = self.bus.recv()
            if response:
                print("[INFO] Received response:", list(response.data))
                print("[DEBUG] Binary:", [bin(b) for b in response.data])

                raw, physical = self.decode_signal(response.data, 8, 1)
                print("LED Status",physical)
                self.LED_status = bool(physical)
                if self.LED_status == 0:
                    self.LED_status = True
                print("[INFO] LED_status:", self.LED_status)

                self.update_014_singal.emit(self.LED_status)
            else:
                print("[WARN] Timeout waiting for CAN response (0x014 LED OFF)")

        except can.CanError as e:
            print(f"[ERROR] CAN error: {str(e)}")

        finally:
            self.busy = False

    def fun_0x014_LED_ON(self, retry_mode=False):
        print('[INFO] Inside 0x014 LED ON function')
        if self.busy:
            print("[WARN] System is busy, please wait...")
            return

        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("[INFO] PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"[ERROR] CAN bus init failed: {str(e)}")
                return

        self.busy = True

        try:
            # LED ON command
            msg = can.Message(arbitration_id=0x014, data=[0, 1, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)
            print("[INFO] Sent LED ON message:", msg.data)

            response = self.bus.recv()
            print("Response", response.data)
            if response:

                print("[INFO] Received response:", list(response.data))
                print("[DEBUG] Binary:", [bin(b) for b in response.data])

                raw, physical = self.decode_signal(response.data, 8, 1)
                print("LED Status", physical)
                self.LED_status = bool(physical)
                if self.LED_status == 1:
                    self.LED_status = True
                print("[INFO] LED_status:", self.LED_status)

                self.update_014_singal.emit(self.LED_status)
            else:
                print("[WARN] Timeout waiting for CAN response (0x014 LED ON)")

        except can.CanError as e:
            print(f"[ERROR] CAN error: {str(e)}")

        finally:
            self.busy = False

    def display_0x014(self):
        self.ui.plainTextEdit_30.setPlainText(str(self.LED_status))

        self.ui.textEdit.append(f"LED status: {str(self.LED_status)}")


    def fun_0x015(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy
        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x015, data=[0, 1, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)

            # Wait for a response
            message = self.bus.recv()  # You can add a timeout, e.g., self.bus.recv(2.0)
            print("IGN Status", message)

            # if message:
            #     # Pass the full data array instead of just one byte
            #     self.IGN_result = self.decode_signal(message.data, 8, 1)
            #     self.IGN_result = self.IGN_result[0]
            #     print('IGN Status :', self.IGN_result)
            #     self.update_015_singal.emit(str(self.IGN_result))
            #
            #     # Call relay control based on ignition state
            #     # If ignition is on (1), turn relay on. If ignition is off (0), turn relay off.
            #     if self.IGN_result == 1:
            #         # Call control_usb_relay to turn the relay on (e.g., relay_number 1, state 1 for on)
            #         self.control_usb_relay(port=self.relay_port, relay_number=1, state=1)
            #     elif self.IGN_result == 0:
            #         # Call control_usb_relay to turn the relay off (e.g., relay_number 1, state 0 for off)
            #         self.control_usb_relay(port=self.relay_port, relay_number=1, state=0)
            # else:
            #     print(f"Timeout waiting for message for CAN ID 0x015. No response received.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            if self.bus:
                self.bus.shutdown()
                self.bus = None

    def display_0x015(self):
        self.ui.plainTextEdit_28.setPlainText(str(self.IGN_result))

        self.ui.textEdit.append(f"IGN Status: {self.IGN_result}")


    def fun_0x122(self,retry_mode =False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=250000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            
            # Create the CAN message
            msg = can.Message(arbitration_id=0x122, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message once
            self.bus.send(msg)

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv(timeout=2)  # 2 seconds timeout for response

            if message:
               
                self.watchdog_reboot = message.data[1]
                print('Watchdog reboot status:', self.watchdog_reboot)

                if self.watchdog_reboot != 1:
                    self.watchdogreboot_flag = False
                    
                else:
                    self.watchdogreboot_flag = True
                    self.update_122_signal.emit(self.reboot_str)
                    # self.retry_timer = QTimer(self)
                    # self.retry_timer.timeout.connect(self.update_rebootStatus)
                    # self.retry_timer.setSingleShot(True)
                    # self.retry_timer.start(1000)
                    
            else:
                # If no message is received within the timeout period
                print(f"Timeout waiting for message for CAN ID 0x102. No response received.")


        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            print('inside finally block')
            received_frames[0x122].clear()  # Clear any frames in the buffer for ID 0x102
            self.function122_done = True
            self.retry_timer = QTimer(self)
            self.retry_timer.timeout.connect(self.fun_0x123)
            self.retry_timer.setSingleShot(True)
            self.retry_timer.start(45000)
            #time.sleep(2)  # Sleep to allow processing
            
            #self.execute_next_function()  # Move on to the next function

    # def update_rebootStatus(self):
    #     self.ui.plainTextEdit_12.setPlainText(" Please wait device is rebooting...")
    #     self.ui.plainTextEdit_12.setStyleSheet("""
    #         font-size: 16px; 
    #         font-weight: bold; 
    #         color: red;
    #     """)

    
    def fun_0x123(self,retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=250000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return
            
        self.busy = True  # Mark the system as busy

        # Initialize previous watchdog count if it doesn't exist
        if not hasattr(self, 'prev_watchdog_reboot_count_dec'):
            self.prev_watchdog_reboot_count_dec = None
        try:
            # Create the CAN message
            msg = can.Message(arbitration_id=0x123, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            
            # Send the message once
            self.bus.send(msg)
            print('123 send msg',msg)

            # Wait for a response with a timeout (e.g., 2 seconds)
            message = self.bus.recv(timeout=2)  # 2 seconds timeout for response

            if message:
                print('received 123 hex msg',message)
                # Update the current watchdog reboot count with new data
                self.watchdog_reboot_count = message.data[1:5]
                self.watchdog_reboot_count_dec = int.from_bytes(self.watchdog_reboot_count, byteorder='big')
                print('Current watchdog reboot count decimal:', self.watchdog_reboot_count_dec)
                # Compare with previous count
                if self.prev_watchdog_reboot_count_dec is not None:
                    print('Previous watchdog reboot count decimal:', self.prev_watchdog_reboot_count_dec)
                    if self.watchdog_reboot_count_dec > self.prev_watchdog_reboot_count_dec:
                        self.watchdogrebootCount_flag = True
                        print("Watchdog reboot count is incremental as expected.")
                    elif self.watchdog_reboot_count_dec == self.prev_watchdog_reboot_count_dec:
                        self.watchdogrebootCount_flag = False
                        print("Error: Watchdog reboot count is the same as the previous count.")
                    else:
                        print("Error: Watchdog reboot count has decreased, which is unexpected!")
                else:
                    print("No previous watchdog reboot count available for comparison.")
                    # print("\n")
                    # print("########## Device reboot Starting #########")
                    # print(" Please wait device is rebooting...")

                # Update the previous watchdog reboot count
                self.prev_watchdog_reboot_count_dec = self.watchdog_reboot_count_dec
                self.fun123_checkedin +=1
                if self.fun123_checkedin ==2:
                    self.fun123_checkedin =0

                    self.update_123_singal.emit(self.watchdogreboot_flag ,self.watchdogrebootCount_flag,self.watchdog_reboot_count_dec)

                    


                else:
                    pass

            else:
                
                self.update_123_singal.emit(self.watchdogreboot_flag ,self.watchdogrebootCount_flag,self.watchdog_reboot_count_dec)



        finally:
                self.busy = False  # Mark the system as not busy
                self.function123_done = True
                if self.bus:  # Ensure we properly shut down the bus
                    self.bus.shutdown()  # Properly shut down the bus
                    self.bus = None  # Set bus to None
                received_frames[0x123].clear()  # Clear any frames in the buffer for ID 0x102
                if not retry_mode:  # Skip calling execute_next_function during retries
                    self.execute_next_function()



    # def DIs_func(self):
    #         if self.busy:  # Check if the system is busy
    #             print("System is busy, please wait...")
    #             return

    #         if self.bus is None:  # Check if the bus was initialized properly
    #             print("CAN Bus not initialized. Cannot send message.")
    #             return

    #         self.busy = True  # Mark the system as busy

    #         try:
    #             # Create the CAN message
    #             msg = can.Message(arbitration_id=0x119, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

    #             # Send the message once
    #             self.bus.send(msg)

    #             # Wait for a response with a timeout (e.g., 2 seconds)
    #             message = self.bus.recv(timeout=2)  # 2 seconds timeout for response

    #             if message:
    #                 self.IGN = message.data[1]
    #                 print('IGN :', self.IGN)

    #                 self.tamper = message.data[2]
    #                 self.ui.Tamp_L.setPlainText(str(self.tamper))
    #                 print('Tamper:', self.tamper)

    #                 self.DI1 = message.data[3]
    #                 print('DI1 :', self.DI1)

    #                 self.DI2 = message.data[4]
    #                 print('DI2 :', self.DI2)

    #                 self.DI3 = message.data[5]
    #                 print('DI3 :', self.DI3)

    #             else:
    #                 # If no message is received within the timeout period
    #                 print(f"Timeout waiting for message for CAN ID 0x119. No response received.")

    #             if self.tamper != 0:
    #                 self.ui.Tamp_L.setStyleSheet("background-color : red")
    #                 self.ui.plainTextEdit_47.setPlainText("Fail")
    #                 self.ui.plainTextEdit_47.setStyleSheet("""Font-size:16px; font-weight: Bold; background-color: red""")
    #             else:
    #                 self.ui.Tamp_L.setStyleSheet("background-color : white")
    #                 self.ui.plainTextEdit_47.setPlainText("Pass")
    #                 self.ui.plainTextEdit_47.setStyleSheet("""Font-size:16px; font-weight: Bold; background-color: green""")

    #             self.Tamper_result = self.ui.plainTextEdit_47.toPlainText()

    #             # Update UI fields if they are empty
    #             if not self.ui.DI1_H_3.toPlainText():
    #                 self.ui.DI1_H_3.setPlainText(str(self.IGN))

    #             else:
    #                 self.ui.IGN_H.setPlainText(str(self.IGN))

    #             if not self.ui.DI1_H_6.toPlainText():
    #                 self.ui.DI1_H_6.setPlainText(str(self.DI1))
    #             else:
    #                 self.ui.DI1_H_7.setPlainText(str(self.DI1))

    #             if not self.ui.DI1_H_4.toPlainText():
    #                 self.ui.DI1_H_4.setPlainText(str(self.DI2))
    #             else:
    #                 self.ui.DI1_H_5.setPlainText(str(self.DI2))

    #             if not self.ui.DI1_H_8.toPlainText():
    #                 self.ui.DI1_H_8.setPlainText(str(self.DI3))
    #             else:
    #                 self.ui.DI_H.setPlainText(str(self.DI3))

    #             self.ui.plainTextEdit_12.appendPlainText(f"IGN: {str(self.IGN)}\n")
    #             self.ui.plainTextEdit_12.appendPlainText(f"Tamper: {str(self.tamper)}\n")
    #             self.ui.plainTextEdit_12.appendPlainText(f"DI1,DI2,DI3: {self.DI1}, {self.DI2}, {self.DI3}")

    #             # Track whether we have seen both states (0 and 1) for each DI
    #             # Check and update DI1 status
    #             if self.DI1 == 0:
    #                 self.DI1_seen_0 = True  # Mark that we have seen 0 for DI1
    #             elif self.DI1 == 1:
    #                 self.DI1_seen_1 = True  # Mark that we have seen 1 for DI1

    #             # Check and update DI2 status
    #             if self.DI2 == 0:
    #                 self.DI2_seen_0 = True  # Mark that we have seen 0 for DI2
    #             elif self.DI2 == 1:
    #                 self.DI2_seen_1 = True  # Mark that we have seen 1 for DI2

    #             # Check and update DI3 status
    #             if self.DI3 == 0:
    #                 self.DI3_seen_0 = True  # Mark that we have seen 0 for DI3
    #             elif self.DI3 == 1:
    #                 self.DI3_seen_1 = True  # Mark that we have seen 1 for DI3

    #             if self.IGN == 0:
    #                 self.IGN_seen_0 =True
    #             else:
    #                 self.IGN_seen_1 = True

    #             # Use QTimer to periodically check if both 0 and 1 have been seen for each DI
    #             self.timer = QTimer(self)
    #             self.timer.setInterval(1000)  # 1000 ms = 1 second
    #             self.timer.timeout.connect(self.check_flags)  # Connect timeout to the check_flags function
    #             self.timer.start(1000)  # Check every second (1000 ms)

    #         except can.CanError as e:
    #             print(f"CAN error: {str(e)}")

    #         finally:
    #             self.busy = False  # Mark the system as not busy
    #             received_frames[0x119].clear()
    #             self.DIs_func_done = True
    #             time.sleep(2)


    # def check_flags(self):
    #     # This method will be called every second
    #     #print(f"Checking flags: DI1_seen_0={self.DI1_seen_0}, DI1_seen_1={self.DI1_seen_1}, DI2_seen_0={self.DI2_seen_0}, DI2_seen_1={self.DI2_seen_1}, DI3_seen_0={self.DI3_seen_0}, DI3_seen_1={self.DI3_seen_1}")

    #     # Now check if all flags are True
    #     if self.DI1_status and self.DI2_status and self.DI3_status:
    #         self.timer.stop()  # Stop the timer when all flags are True
    #         print('timer stopped')
        
    #         # Now that all DI states are confirmed (both 0 and 1), determine the result
    #         if self.DI1_status and self.DI2_status and self.DI3_status:
    #             self.ui.plainTextEdit_22.setPlainText("Pass")
    #             self.ui.plainTextEdit_22.setStyleSheet("""Font-size:16px; font-weight: Bold; background-color: green""")
    #         else:
    #             self.ui.plainTextEdit_22.setPlainText("Fail")
    #             self.ui.plainTextEdit_22.setStyleSheet("""Font-size:16px; font-weight: Bold; background-color: red""")
        

    #     if self.IGN_seen_0 and self.IGN_seen_1:
    #         self.timer.stop()
    #         if self.IGN_seen_0 and self.IGN_seen_1:

    #             self.ui.plainTextEdit_26.setPlainText("Pass")
    #             self.ui.plainTextEdit_26.setStyleSheet("""Font-size:16px; font-weight: Bold; background-color: green""")
    #         else:
    #             self.ui.plainTextEdit_26.setPlainText("Fail")
    #             self.ui.plainTextEdit_26.setStyleSheet("""Font-size:16px; font-weight: Bold; background-color: red""")
    
    #     self.DIs_result = self.ui.plainTextEdit_22.toPlainText()
    #     self.IGN_result = self.ui.plainTextEdit_26.toPlainText()




    def showpopup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def extract_bits_motorola(self, data, start_bit, length):
        print("data......", data)

        # Ensure data is a list of integers
        if isinstance(data[0], str):
            data = [int(byte, 16) for byte in data]
            return data
            # Now it's safe to assume data is indexable (like list or string)
        if isinstance(data, (list, tuple)) and len(data) > 0:
                if isinstance(data[0], str):
                    data = [int(byte, 16) for byte in data]
                    return data
        raw = 0
        for i in range(length):
            bit_index = start_bit + i
            print("bit_index", bit_index)
            byte_index = bit_index // 8
            print("byte_index", byte_index)
            bit_in_byte = 7 - (bit_index % 8)
            print("bit_in_byte", bit_in_byte)

            # Perform bitwise extraction correctly
            bit_val = (data[byte_index] >> bit_in_byte) & 1
            print("data", data)
            print("bit_val", bit_val)
            raw = (raw << 1) | bit_val
            print("raw", raw)
        print("Raw", raw)
        return raw

    def decode_signal(self, data, start_bit, length, factor=1.0, offset=0.0):
        raw_val = self.extract_bits_motorola(data, start_bit, length)
        physical_val = raw_val * factor + offset
        print("physical_val",physical_val)
        return raw_val, int(physical_val)

    def hex_string_to_byte_array(self, hex_string):
        hex_string = hex_string.strip().replace(" ", "")
        if len(hex_string) % 2 != 0:
            raise ValueError("Hex string must contain an even number of characters.")
        return bytes.fromhex(hex_string)

    def print_binary_stream(self, payload):
        print("\nBinary Payload Stream:")
        for byte in payload:
            print(format(byte, '08b'), end=' ')
        print()

    def find_relay_port(self):
        """Automatically find the USB relay module's serial port"""
        ports = serial.tools.list_ports.comports()

        for port in ports:
            # Check for common USB relay characteristics
            if (port.vid == 0x1A86 and port.pid == 0x7523) or \
                    (port.vid == 0x0403 and port.pid == 0x6001) or \
                    "USB Relay" in str(port.description) or \
                    "USB-SERIAL" in str(port.description):
                return port.device

        return None

    def control_usb_relay(self, port, relay_number, state):
        """Control a USB relay module"""
        try:
            with serial.Serial(port, baudrate=9600, timeout=1) as ser:
                command = bytes([0xFF, relay_number, state])
                ser.write(command)
                print(f"Relay {relay_number} turned {'on' if state else 'off'}")
        except Exception as e:
            print(f"Error controlling relay: {e}")

    #
    def fun_0x01(self, retry_mode=False):
        if self.busy:
            print("System is busy, please wait...")
            return

        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                self.showpopup("Error initializing CAN bus")
                return

        self.busy = True

        try:
            # Send 0x01 CAN message
            msg = can.Message(arbitration_id=0x01, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)
            print("send 0x01 msg", msg)

            # Receive response
            self.message = self.bus.recv(timeout=5)
            print("IGN 0x01 Response", self.message)

            try:
                if self.message:
                    print("Full data hex:", self.message.data.hex())
                    print("Message length:", len(self.message.data))
                    data = self.message.data

                    # Decode ignition signal (bit 7, 1-bit length)
                    if len(data) >= 1:
                        ign_raw, ign = self.decode_signal(data, 7, 1)
                        print("ign_raw, ign", ign_raw, ign)
                        self.IGN = ign
                    else:
                        print("Message too short for ignition signal.")
                        self.IGN = 0

                    # Decode timestamp (starting at bit 9, 32 bits)
                    if len(data) >= 6:  # Requires at least 6 bytes
                        raw_time, decoded_time = self.decode_signal(data, 9, 32)
                        self.Time = decoded_time
                        print("Decoded time (epoch seconds):", self.Time)

                        self.readable_time = datetime.fromtimestamp(self.Time, timezone.utc)
                        print("Readable time:", self.readable_time)
                    else:
                        print("Message too short to extract timestamp.")
                        self.readable_time = "N/A"

                    # Decode mains voltage (starting at bit 42, 16 bits)
                    if len(data) >= 7:
                        mains_vtg_tuple = self.decode_signal(data, 42, 16)
                        self.mains_vtg = mains_vtg_tuple[1] / 1000
                        print("Mains vtg (raw):", float(self.mains_vtg))
                    else:
                        print("Message too short to extract mains voltage.")
                        self.mains_vtg = 0

                    # Emit signal if all data is valid
                    self.update_01_singal.emit(str(self.readable_time), str(self.IGN), str(self.mains_vtg))



            except can.CanError as e:
                print(f"CAN error: {str(e)}")

            finally:
                self.busy = False
                self.function108_done = True
                received_frames[0x01].clear()
                if self.bus:
                    self.bus.shutdown()
                    self.bus = None

        finally:
            pass

    def display_0x01(self):
        self.ui.textEdit.append(f"Ignition Status: {str(self.IGN)}")
        # self.ui.plainTextEdit_10.setPlainText(str(self.IGN))
        # Update UI with both Ignition Status and Time
        self.ui.textEdit.append(f"Ignition Time: {self.readable_time}")
        self.ui.textEdit.append(f"Mains Vtg: {self.mains_vtg}")
        self.ui.plainTextEdit_12.setPlainText(str(self.mains_vtg))

    def fun_0x05(self, retry_mode=False):
        if self.busy:  # Check if the system is busy
            print("System is busy, please wait...")
            return

        if self.bus is None:  # Check if the bus is not initialized
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                return

        self.busy = True  # Mark the system as busy

        try:
            msg = can.Message(arbitration_id=0x05, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

            # Send the message
            self.bus.send(msg)

            # Wait for the response
            for i in range(expected_frame_counts[0x05]):
                message = self.bus.recv(timeout=2)  # 2 second timeout for each frame
                if message:
                    received_frames[0x05].append(message)

                else:
                    print(f"Timeout waiting for message for CAN ID 0x04. No response received.")

            # Check if we have received all expected frames for 0x013
            if len(received_frames[0x05]) == expected_frame_counts[0x05]:
                frames = received_frames[0x05]
                frames.sort(key=lambda x: x.data[0])

                complete_message = b''.join(frame.data[0:] for frame in frames)
                print("complete_message", complete_message)
                alti = self.decode_signal(complete_message, 8, 32)

                print("Alti", alti)
                # print("Alti", alti)
                try:
                    if alti:
                        # self.latitude = latitude.decode('ascii')

                        self.alti = alti[0]*10_000_000
                        print("Inside try", alti)
                        self.update_05_singal.emit(self.alti)
                        print("altitude:", self.alti)
                        # Create the model with two columns

                except UnicodeDecodeError:
                    print("Error decoding latitude to ASCII. The data may contain non-ASCII characters.")
            else:
                print(
                    f"Not all frames received for CAN ID 0x05. Expected {expected_frame_counts[0x05]}, but received {len(received_frames[0x05])}.")

        except can.CanError as e:
            print(f"CAN error: {str(e)}")

        finally:
            self.busy = False  # Mark the system as not busy
            # self.function013_done = True
            if self.bus:  # Ensure we properly shut down the bus
                self.bus.shutdown()  # Properly shut down the bus
                self.bus = None  # Set bus to None
            received_frames[0x05].clear()
            if not retry_mode:  # Skip calling execute_next_function during retries
                self.execute_next_function()

    def display_0x05(self):
        self.ui.plainTextEdit_24.setPlainText(str(self.alti))

        self.ui.textEdit.append(f"Altitude: {self.alti}")




    def execute_next_function(self):
        """Check which function is done and call the next one."""
        # if self.function103_done and not self.function104_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x104)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function104_done and not self.function106_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x106)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function106_done and not self.function105_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x105)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function105_done and not self.function101_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x101)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function101_done and not self.function100_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x013)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function100_done and not self.function110_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x110)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function110_done and not self.function112_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x112)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function112_done and not self.function109_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x109)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function109_done and not self.function115_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x115)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function115_done and not self.function116_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x116)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        #
        # elif self.function116_done and not self.function113_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x113)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function113_done and not self.function114_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x114)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function114_done and not self.function102_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x102)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function102_done and not self.function121_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x121)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function121_done and not self.function119_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x119)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)

        # elif self.function119_done and not self.function108_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x01)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #self.fun_0x01()

        # elif self.function108_done and not self.function123_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x123)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
        #
        # elif self.function123_done and not self.function122_done:
        #     self.retry_timer = QTimer(self)
        #     self.retry_timer.timeout.connect(self.fun_0x122)
        #     self.retry_timer.setSingleShot(True)
        #     self.retry_timer.start(1000)
            
        # else:
        #     print("All functions completed.")
        #     # You can enable a button or perform other tasks once all functions are done

    def rearrange_message(self, collected_bytes: bytearray) -> str:
        data_bytes = bytes(collected_bytes)
        try:
            raw_str = data_bytes.decode(errors='replace')
        except Exception:
            raw_str = data_bytes.decode(errors='ignore')

        # Normalize line endings
        raw_str = raw_str.replace('\r\n', '\n').replace('\r', '\n')

        # Remove duplicates and strip whitespace
        seen = set()
        ordered_lines = []
        for line in raw_str.split('\n'):
            line = line.strip()
            if line and line not in seen:
                ordered_lines.append(line)
                seen.add(line)

        return '\n'.join(ordered_lines)

    def receive_can_message(self, bus, timeout=40, frame_timeout=5, min_linebreaks=4):
        """
        Receives multiple CAN frames from the bus and accumulates their data
        until a minimum number of line breaks are detected or timeout occurs.

        Returns the accumulated bytes as a bytearray.
        """
        collected_bytes = bytearray()
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print("Overall timeout reached.")
                break

            frame = bus.recv(timeout=frame_timeout)
            if frame is None:
                print(f"No frame received within {frame_timeout} seconds.")
                break

            print(f"Received frame ID=0x{frame.arbitration_id:X}, data={frame.data.hex()}")
            collected_bytes.extend(frame.data)

            # Show partial ascii message so far, ignoring decode errors
            try:
                partial_msg = collected_bytes.decode(errors='replace')
                print("Partial message so far:", partial_msg)
            except Exception:
                pass

            if collected_bytes.count(b'\r\n') >= min_linebreaks:
                print(f"Detected {min_linebreaks} line breaks, assuming full message received.")
                break

        return collected_bytes

    def initialize_bus(self):
        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                self.showpopup("Error initializing CAN bus")

    def fun_0x21(self, retry_mode=False):
        if self.busy:
            print("System is busy, please wait...")
            return
        self.stop_receiving = False
        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                self.showpopup("Error initializing CAN bus")
                return

        self.busy = True
        try:
            # Send the 0x21 request
            msg = can.Message(arbitration_id=0x21, data=[0, 1, 0, 0, 0, 0, 0, 0], is_extended_id=False)
            self.bus.send(msg)
            print("Request message sent:", msg)

            collected_bytes = bytearray()
            print("Listening for incoming frames until stop_receiving is True...")

            while not self.stop_receiving:
                msg = self.bus.recv(timeout=1)  # 1 second to prevent blocking forever

                if msg is None:
                    continue  # No message received, check stop flag again

                print("Received frame:", msg)
                collected_bytes.extend(msg.data)

                # Decode and emit
                try:
                    self.decoded_so_far = collected_bytes.decode(errors='replace')
                except UnicodeDecodeError:
                    self.decoded_so_far = ""

                rearranged = self.rearrange_message(bytes(collected_bytes))
                now = datetime.now()
                timestamp = f"[{now.strftime('%Y-%m-%d %H:%M:%S')}.{now.microsecond // 1000:03d}]"

                self.rearranged_message = f"{timestamp}{rearranged}"
                self.update_21_singal.emit(self.rearranged_message)  # Make sure signal name is correct!
                self.save_data()
                QApplication.processEvents()  # Keeps UI responsive

                print("Rearranged msg:", self.rearranged_message)

                # Optional: stop automatically if full message received
                if "System initialized at" in self.decoded_so_far and self.decoded_so_far.strip().endswith("\r\n"):
                    print("Detected full message block.")
                    break

        finally:
            self.busy = False
            self.function108_done = True
            if self.bus:
                self.bus.shutdown()
                self.bus = None




    def display_0x21(self, message: str):
        print("display_0x21 called with message:", message)
        self.ui.textEdit.append(message)

    def shutdown_can(self):
        # First shut down python-can
        if self.bus is not None:
            try:
                self.bus.shutdown()
                print("python-can bus shutdown called.")
            except Exception as e:
                print(f"Error shutting down python-can bus: {str(e)}")
            finally:
                self.bus = None

        # Then uninitialize PCAN directly via PCANBasic
        result = self.pcan.Uninitialize(PCAN_USBBUS1)
        if result == PCAN_ERROR_OK:
            print("PCANBasic bus uninitialized successfully.")
        else:
            print(f"PCANBasic uninitialization failed with error code: {hex(result)}")
    def stop_debug(self):
        print("Stop button clicked...")
        if self.bus is None:
            try:
                self.bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
                self.stop_receiving = True
                print("PCAN bus initialized successfully.")
            except can.CanError as e:
                print(f"Error initializing CAN bus: {str(e)}")
                self.showpopup("Error initializing CAN bus")
                return
        msg = can.Message(arbitration_id=0x21, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
        self.bus.send(msg)
        print("Stop debug called")
        print("Request message sent:", msg)

    def save_data(self):
        try:
            # Choose your path and filename here
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f"can_data_log_{current_date}.txt"

            with open(filename, "a", encoding="utf-8") as f:
                f.write(self.rearranged_message + "\n")

            print(f"Data saved to {filename}")

        except Exception as e:
            print(f"Error saving data: {e}")
            self.showpopup(f"Error saving data: {e}")

    def retry_iteration(self):
        if self.retry >= 3:
            print("Max retries reached. Stopping...")
            self.retry_str_flag = False
            self.max_retries_flag = True
            self.update_retryUI_signal.emit(self.retry_str_flag, self.max_retries_flag)
            self.retry_timer.stop()
            return

        print(f"Starting retry iteration {self.retry + 1}...")

        any_function_passed = False  # Track if any function passes during this iteration

        # Iterate through the functions in the failure list
        for func in list(self.failFunc_list):  # Using list() to avoid modifying the list while iterating
            # Check if the function has passed already
            if self.is_flag_passed(func):
                print(f"Function {func.__name__} already passed. Skipping...")
                self.failFunc_list.remove(func)  # Remove passed functions from the retry list
                continue

            try:
                # Retry the function (pass `retry_mode=True` to prevent execution of next function)
                success = func(retry_mode=True)  # If successful, function should return True
                if success:
                    print(f"Function {func.__name__} passed.")
                    self.update_flag(func, 'Pass')  # Update the flag to "Pass"
                    self.failFunc_list.remove(func)  # Remove from the failure list
                    any_function_passed = True  # Mark that a function passed
            except Exception as e:
                print(f"Error while calling {func.__name__}: {e}")
                continue

        # If any function passed before 3 retries, stop retries immediately
        if any_function_passed or not self.failFunc_list:
            print("All functions succeeded before 3 retries. Stopping retries immediately.")
            self.retry_str_flag = False
            self.max_retries_flag = True
            self.update_retryUI_signal.emit(self.retry_str_flag, self.max_retries_flag)  # Update UI immediately
            self.retry_timer.stop()  # Stop the retry timer
            return  # Explicit return to prevent further execution

        # Move retry increment before next iteration
        self.retry += 1

    def clean_string(self, value):
        """Clean string: trim, unescape HTML, remove control characters, and handle None."""
        if value is None:
            return 'Not found'

        # Convert to string and strip whitespace
        value = str(value).strip()

        # Unescape HTML entities (e.g., &amp; -> &)
        value = html.unescape(value)

        # Remove control characters and non-printable characters
        value = re.sub(r'[\x00-\x1F\x7F]', '', value)

        # Optional: remove non-ASCII characters
        # value = re.sub(r'[^\x00-\x7F]+', '', value)

        # Optional: remove HTML tags
        # value = re.sub(r'<[^>]*>', '', value)

        return value

    def save_to_excel(self):
        print("Save to excel called...")

        # Define the filename directly here
        filename = 'A2T debug data.xlsx'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Clean application version and IMEI strings or set to 'Not found' if None
        App_fw_version = [self.clean_string(self.appln_ver) if self.appln_ver is not None else 'Not found']
        IMEI = [self.clean_string(self.IMEI_Str) if self.IMEI_Str is not None else 'Not found']
        gsm_status = [self.clean_string(self.GSM_status) if self.GSM_status is not None else 'Not found']
        No_of_satelite = [self.clean_string(self.concatenated_hex) if self.concatenated_hex is not None else 'Not found']
        mains_vtg =   [self.clean_string(self.mains_vtg) if self.mains_vtg is not None else 'Not found']
        lat = [self.clean_string(self.latitude) if self.latitude is not None else 'Not found']
        hdop = [self.clean_string(self.hdop) if self.hdop is not None else 'Not found']
        bl_fw_version = [self.clean_string(self.BL_ver) if self.BL_ver is not None else 'Not found']
        iccid = [self.clean_string(self.ICCID_string) if self.ICCID_string is not None else 'Not found']
        gps_status = [self.clean_string(self.Gps_status) if self.Gps_status is not None else 'Not found']
        operator = [self.clean_string(self.operatorName) if self.operatorName is not None else 'Not found']
        ign_status = [self.clean_string(self.IGN) if self.IGN is not None else 'Not found']
        longitude = [self.clean_string(self.long) if self.long is not None else 'Not found']
        pdop = [self.clean_string(self.pdop) if self.pdop is not None else 'Not found']
        cource = [self.clean_string(self.cource) if self.cource is not None else 'Not found']
        csq = [self.clean_string(self.CSQ) if self.CSQ is not None else 'Not found']
        gps_fix_time = [self.clean_string(self.ActualTime) if self.ActualTime is not None else 'Not found']
        can_status = [self.clean_string(self.CAN_status) if self.CAN_status is not None else 'Not found']
        alt = [self.clean_string(self.alti) if self.alti is not None else 'Not found']
        led_status = [self.clean_string(self.LED_status) if self.LED_status is not None else 'Not found']
        aepl_mqtt = [self.clean_string(self.AEPL_MQTT) if self.AEPL_MQTT is not None else 'Not found']
        login_pkt_status = [self.clean_string(self.AEPL_lgn_pkt) if self.AEPL_lgn_pkt is not None else 'Not found']
        # Create a dictionary with the data
        data = {
            'Application Firmware Version': App_fw_version,
            "Bootloader Firmware Version": bl_fw_version,
            'IMEI': IMEI,
            'ICCID': iccid,
            'GSM Status': gsm_status,
            'No. of Satelite': No_of_satelite,
            'Mains voltage': mains_vtg,
            'Latitude': lat,
            'HDOP': hdop,
            'GPS Status': gps_status,
            'Operator': operator,
            'Ignition': ign_status,
            'Longitude': longitude,
            'PDOP':pdop,
            'Cource': cource,
            'CSQ': csq,
            'GPS Fix Time': gps_fix_time,
            'CAN Status During IGN On': can_status,
            'Altitude': alt,
            'LED Status': led_status,
            'AEPL MQTT Connection': aepl_mqtt,
            'Login Packet Status': login_pkt_status,
            'Timestamp': [current_time]
        }

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)

        # Save the DataFrame to an Excel file at the current location
        try:
            df.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
            self.showpopup("Data saved to Excel")
        except Exception as e:
            print(f"An error occurred while saving to Excel: {e}")

def main():
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
        
    


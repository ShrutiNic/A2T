import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import can
import cantools
import threading
import time
import requests
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import webbrowser
from datetime import datetime

# Global variables
db = None
bus = None
selected_ids = {}
spn_entries = {}
sending = False
send_thread = None
odometer_tx_value = 0
speed_tx_value = 0

# Constants
ODOMETER_MAX = 16777214
VEHICLE_SPEED_MAX = 127.96875
TRANSMIT_INTERVAL = 10  # seconds
API_REFRESH_INTERVAL = 10  # seconds
VALIDATE_INTERVAL = 10  # 10 milliseconds


class CANTransmitter:
    def __init__(self):
        self.bus = None
        self.initialize_pcan()

    def initialize_pcan(self):
        try:
            self.bus = can.interface.Bus(
                channel='PCAN_USBBUS1',
                interface='pcan',
                bitrate=500000,
                receive_own_messages=True
            )
            return True
        except Exception as e:
            messagebox.showerror("PCAN Error", f"Failed to initialize PCAN:\n{e}")
            return False

    def send_message(self, msg):
        if not self.bus:
            return False
        try:
            self.bus.send(msg)
            return True
        except Exception as e:
            print(f"Transmission error: {e}")
            return False

    def shutdown(self):
        if self.bus:
            self.bus.shutdown()


class ModernUI:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.transmitter = CANTransmitter()

        # Counters
        self.tx_count = 0
        self.rx_count = 0
        self.error_count = 0

        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 10))

        # Variables
        self.auto_increment_odo = tk.BooleanVar(value=False)
        self.auto_increment_speed = tk.BooleanVar(value=False)
        self.can_id_var = tk.StringVar()
        self.vin_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Status: Disconnected")
        self.tx_count_var = tk.StringVar(value="Messages Sent: 0")
        self.rx_count_var = tk.StringVar(value="Messages Received: 0")
        self.error_count_var = tk.StringVar(value="Errors: 0")

        # Status bar
        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(status_bar, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Label(status_bar, textvariable=self.tx_count_var).pack(side=tk.LEFT, padx=20)
        ttk.Label(status_bar, textvariable=self.rx_count_var).pack(side=tk.LEFT, padx=20)
        ttk.Label(status_bar, textvariable=self.error_count_var).pack(side=tk.LEFT, padx=20)

        # Main content frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Left panel - Configuration
        left_panel = ttk.Frame(main_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Configuration notebook
        config_notebook = ttk.Notebook(left_panel)
        config_notebook.pack(fill=tk.BOTH, expand=True)

        # DBC Configuration tab
        dbc_tab = ttk.Frame(config_notebook)
        config_notebook.add(dbc_tab, text="DBC Configuration")

        tk.Button(
            dbc_tab,
            text="Load DBC File",
            command=self.browse_dbc_file,
            bg="#2196F3",
            fg="Black",
            font=('Segoe UI', 10),
            relief=tk.FLAT
        ).pack(fill=tk.X, pady=5)

        ttk.Label(dbc_tab, text="Select CAN ID:").pack(anchor='w', pady=(8, 0))
        self.can_id_dropdown = ttk.Combobox(dbc_tab, textvariable=self.can_id_var, state="readonly")
        self.can_id_dropdown.bind("<<ComboboxSelected>>", self.update_spn_fields)
        self.can_id_dropdown.pack(fill=tk.X, pady=3)

        # Signals frame with scrollbar
        signals_frame = ttk.Frame(dbc_tab)
        signals_frame.pack(fill=tk.BOTH, expand=True, pady=3)

        canvas = tk.Canvas(signals_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(signals_frame, orient="vertical", command=canvas.yview)
        self.spn_frame = ttk.Frame(canvas)

        self.spn_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.spn_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # VIN Configuration tab
        vin_tab = ttk.Frame(config_notebook)
        config_notebook.add(vin_tab, text="VIN & API")

        ttk.Label(vin_tab, text="VIN Number:").pack(anchor='w', pady=(10, 0))
        ttk.Entry(vin_tab, textvariable=self.vin_var).pack(fill=tk.X, pady=5)

        ttk.Button(vin_tab, text="Fetch API Data", command=self.fetch_and_display_odometer).pack(fill=tk.X, pady=5)

        # Selected Messages frame
        selected_frame = ttk.LabelFrame(left_panel, text="Selected Messages")
        selected_frame.pack(fill=tk.BOTH, pady=(8, 0))

        self.selected_listbox = tk.Listbox(selected_frame, height=6, font=('Consolas', 9))
        self.selected_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

        btn_frame = ttk.Frame(selected_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Add", command=self.add_selected_id).pack(side=tk.LEFT, expand=True)
        ttk.Button(btn_frame, text="Remove", command=self.remove_selected_id).pack(side=tk.LEFT, expand=True)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_selected_ids).pack(side=tk.LEFT, expand=True)

        # Control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=6)

        self.start_btn = tk.Button(
            control_frame,
            text="Start Transmission",
            command=self.start_transmission,
            bg='green',
            fg='Black',
            font=('Segoe UI', 10)
        )
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=2)

        self.stop_btn = tk.Button(
            control_frame,
            text="Stop Transmission",
            command=self.stop_transmission,
            bg='Red',
            fg='Black',
            state=tk.DISABLED,
            font=('Segoe UI', 10)
        )
        self.stop_btn.pack(side=tk.LEFT, expand=True, padx=2)

        # Right panel - Output
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Output notebook
        output_notebook = ttk.Notebook(right_panel)
        output_notebook.pack(fill=tk.BOTH, expand=True)

        # CAN Output tab
        can_tab = ttk.Frame(output_notebook)
        output_notebook.add(can_tab, text="CAN Messages")

        self.can_output = ScrolledText(can_tab, wrap=tk.WORD, font=('Consolas', 9))
        self.can_output.pack(fill=tk.BOTH, expand=True)
        self.can_output.tag_config('tx', foreground='blue')
        self.can_output.tag_config('rx', foreground='green')
        self.can_output.tag_config('error', foreground='red')

        # API Output tab
        api_tab = ttk.Frame(output_notebook)
        output_notebook.add(api_tab, text="API Data")

        self.api_output = ScrolledText(api_tab, wrap=tk.WORD, font=('Consolas', 9))
        self.api_output.pack(fill=tk.BOTH, expand=True)
        self.api_output.tag_config('bold', font=('Consolas', 9, 'bold'))
        self.api_output.tag_config('error', foreground='red')

        # Dashboard tab
        dashboard_tab = ttk.Frame(output_notebook)
        output_notebook.add(dashboard_tab, text="Dashboard")

        ttk.Label(dashboard_tab, text="Transmission Statistics", font=('Segoe UI', 12, 'bold')).pack(anchor='w',
                                                                                                     pady=10)

        stats_frame = ttk.Frame(dashboard_tab)
        stats_frame.pack(fill=tk.X, pady=10)

        ttk.Label(stats_frame, text="Messages Sent:").grid(row=0, column=0, sticky='w', padx=10)
        self.tx_count_label = ttk.Label(stats_frame, text="0", font=('Segoe UI', 12, 'bold'))
        self.tx_count_label.grid(row=0, column=1, sticky='w')

        ttk.Label(stats_frame, text="Messages Received:").grid(row=1, column=0, sticky='w', padx=10)
        self.rx_count_label = ttk.Label(stats_frame, text="0", font=('Segoe UI', 12, 'bold'))
        self.rx_count_label.grid(row=1, column=1, sticky='w')

        ttk.Label(stats_frame, text="Transmission Errors:").grid(row=2, column=0, sticky='w', padx=10)
        self.error_count_label = ttk.Label(stats_frame, text="0", font=('Segoe UI', 12, 'bold'))
        self.error_count_label.grid(row=2, column=1, sticky='w')

        # Validate Data tab
        validate_tab = ttk.Frame(output_notebook)
        output_notebook.add(validate_tab, text="Validate Data")

        self.validate_output = ScrolledText(validate_tab, wrap=tk.WORD, font=('Consolas', 9))
        self.validate_output.pack(fill=tk.BOTH, expand=True)
        self.validate_output.tag_config('bold', font=('Consolas', 9, 'bold'))
        self.validate_output.tag_config('match', foreground='green')
        self.validate_output.tag_config('mismatch', foreground='red')
        self.validate_output.tag_config('error', foreground='orange')
        self.validate_output.tag_config('timestamp', foreground='blue')

        # Telemetry Data tab
        telemetry_tab = ttk.Frame(output_notebook)
        output_notebook.add(telemetry_tab, text="Telemetry Data")

        # Control frame for telemetry
        telemetry_control_frame = ttk.Frame(telemetry_tab)
        telemetry_control_frame.pack(fill=tk.X, pady=5)

        self.telemetry_start_btn = ttk.Button(
            telemetry_control_frame,
            text="Start Auto-Refresh",
            command=self.start_telemetry_refresh,
            style='Accent.TButton'
        )
        self.telemetry_start_btn.pack(side=tk.LEFT, padx=5)

        self.telemetry_stop_btn = ttk.Button(
            telemetry_control_frame,
            text="Stop Auto-Refresh",
            command=self.stop_telemetry_refresh,
            style='Stop.TButton',
            state=tk.DISABLED
        )
        self.telemetry_stop_btn.pack(side=tk.LEFT, padx=5)

        self.telemetry_count_label = ttk.Label(
            telemetry_control_frame,
            text="Packets Received at Server: 0",
            font=('Segoe UI', 10, 'bold')
        )
        self.telemetry_count_label.pack(side=tk.RIGHT, padx=10)

        # Telemetry output
        self.telemetry_output = ScrolledText(
            telemetry_tab,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.telemetry_output.pack(fill=tk.BOTH, expand=True)
        self.telemetry_output.tag_config('timestamp', foreground='blue')
        self.telemetry_output.tag_config('count', foreground='green')
        self.telemetry_output.tag_config('error', foreground='red')

        # Telemetry variables
        self.telemetry_refresh = False
        self.telemetry_thread = None
        self.telemetry_packet_count = 0
        self.last_telemetry_data = None
        self.last_telemetry_timestamp = None

        # Auto-validation variables
        self.auto_validate = False
        self.validate_thread = None

        # Configure styles
        self.style.configure('Accent.TButton', foreground='white', background='#4CAF50')
        self.style.configure('Start.TButton', foreground='white', background='#2196F3')
        self.style.configure('Stop.TButton', foreground='white', background='#F44336')
        self.style.map('Accent.TButton', background=[('active', '#45a049')])
        self.style.map('Start.TButton', background=[('active', '#0b7dda')])
        self.style.map('Stop.TButton', background=[('active', '#d32f2f')])

        # Start auto-validation when VIN changes
        self.vin_var.trace_add('write', self.handle_vin_change)

    def setup_ui(self):
        self.root.title("CAN Message Transmitter Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(bg='#f0f0f0')

        # Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Logo and title
        try:
            logo_img = Image.open("logo.png").resize((40, 40))
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=self.logo, bg='#f0f0f0')
            logo_label.pack(side=tk.LEFT, padx=5)
        except:
            pass

        title_label = ttk.Label(header_frame, text="A2T Data Analysis Utility",
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(side=tk.LEFT, padx=550)

    def handle_vin_change(self, *args):
        """Handle changes to VIN field"""
        vin = self.vin_var.get().strip()
        if vin and selected_ids:
            self.start_auto_validation()
        else:
            self.stop_auto_validation()

    def start_auto_validation(self):
        """Start automatic validation of data"""
        if self.auto_validate:
            return

        self.auto_validate = True
        self.validate_thread = threading.Thread(
            target=self.auto_validate_loop,
            daemon=True
        )
        self.validate_thread.start()

    def stop_auto_validation(self):
        """Stop automatic validation of data"""
        self.auto_validate = False
        if self.validate_thread and self.validate_thread.is_alive():
            self.validate_thread.join(0.1)

    def auto_validate_loop(self):
        """Thread function for continuous validation"""
        while self.auto_validate:
            try:
                self.validate_data()
                time.sleep(VALIDATE_INTERVAL)
            except Exception as e:
                self.root.after(0, self.validate_output.insert, tk.END,
                                f"Validation error: {e}\n", 'error')
                time.sleep(VALIDATE_INTERVAL)

    def update_counters(self):
        """Update both status bar and dashboard counters"""
        # Update status bar
        self.tx_count_var.set(f"Messages Sent: {self.tx_count}")
        self.rx_count_var.set(f"Messages Received: {self.rx_count}")
        self.error_count_var.set(f"Errors: {self.error_count}")

        # Update dashboard labels
        self.tx_count_label.config(text=str(self.tx_count))
        self.rx_count_label.config(text=str(self.rx_count))
        self.error_count_label.config(text=str(self.error_count))

    def browse_dbc_file(self):
        file_path = filedialog.askopenfilename(title="Select DBC File", filetypes=[("DBC files", "*.dbc")])
        if file_path:
            try:
                global db
                db = cantools.database.load_file(file_path, strict=False)
                can_ids = sorted([f"0x{msg.frame_id:X}" for msg in db.messages])
                self.can_id_dropdown['values'] = can_ids
                if can_ids:
                    self.can_id_var.set(can_ids[0])
                messagebox.showinfo("Success", "DBC file loaded successfully")
            except Exception as e:
                messagebox.showerror("DBC Load Error", f"Failed to load DBC:\n{e}")

    def update_spn_fields(self, event=None):
        for widget in self.spn_frame.winfo_children():
            widget.destroy()

        spn_entries.clear()

        try:
            can_id = int(self.can_id_var.get(), 16)
        except (ValueError, TypeError):
            return

        if db is None:
            return

        message = db.get_message_by_frame_id(can_id)
        if not message:
            return

        for signal in message.signals:
            row = ttk.Frame(self.spn_frame)
            row.pack(anchor='w', padx=10, pady=2)

            ttk.Label(row, text=signal.name, width=25).pack(side='left')
            entry = ttk.Entry(row, width=15)
            entry.pack(side='left')
            spn_entries[signal.name] = entry

            if signal.unit:
                ttk.Label(row, text=signal.unit).pack(side='left')

            if signal.name == "OdoValDiag":
                ttk.Checkbutton(row, text="Auto Increment", variable=self.auto_increment_odo).pack(side='left')
            elif signal.name == "VehSpdEMS":
                ttk.Checkbutton(row, text="Auto Increment", variable=self.auto_increment_speed).pack(side='left')

    def add_selected_id(self):
        try:
            can_id = int(self.can_id_var.get(), 16)
        except ValueError:
            messagebox.showerror("Error", "Invalid CAN ID format")
            return

        values = {}
        for signal, entry in spn_entries.items():
            val = entry.get().strip()
            try:
                numeric_val = float(val) if val else 0.0
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {signal}")
                return
            values[signal] = numeric_val

        selected_ids[can_id] = values
        self.update_selected_listbox()

        # Start auto-validation if VIN is present
        if self.vin_var.get().strip():
            self.start_auto_validation()

    def update_selected_listbox(self):
        self.selected_listbox.delete(0, tk.END)

        for can_id, signals in selected_ids.items():
            entry_str = f"0x{can_id:X}: "
            signal_strs = []

            for signal, value in signals.items():
                if isinstance(value, float):
                    if value.is_integer():
                        value_str = f"{int(value)}"
                    else:
                        value_str = f"{value:.2f}"
                else:
                    value_str = str(value)

                signal_strs.append(f"{signal}={value_str}")

            entry_str += ", ".join(signal_strs)
            self.selected_listbox.insert(tk.END, entry_str)

    def remove_selected_id(self):
        selected = self.selected_listbox.curselection()
        if selected:
            key = list(selected_ids.keys())[selected[0]]
            del selected_ids[key]
            self.update_selected_listbox()

            # Stop validation if no more selected IDs
            if not selected_ids:
                self.stop_auto_validation()

    def clear_selected_ids(self):
        selected_ids.clear()
        self.update_selected_listbox()
        self.stop_auto_validation()

    def transmit_loop(self):
        global sending, odometer_tx_value, speed_tx_value
        while sending:
            if not self.transmitter.bus:
                print("CAN bus not available - attempting reconnection")
                if not self.transmitter.initialize_pcan():
                    time.sleep(1)
                    continue

            for can_id, signals in selected_ids.items():
                if not sending:
                    break

                # Handle auto-increments
                if self.auto_increment_odo.get() and 'OdoValDiag' in signals:
                    signals['OdoValDiag'] = odometer_tx_value
                    odometer_tx_value = (odometer_tx_value + 5) % (ODOMETER_MAX + 1)

                if self.auto_increment_speed.get() and 'VehSpdEMS' in signals:
                    signals['VehSpdEMS'] = speed_tx_value
                    speed_tx_value = (speed_tx_value + 1) % (VEHICLE_SPEED_MAX + 1)

                try:
                    message = db.get_message_by_frame_id(can_id)
                    data = message.encode(signals)
                    msg = can.Message(
                        arbitration_id=can_id,
                        data=data,
                        is_extended_id=False
                    )

                    if self.transmitter.send_message(msg):
                        self.tx_count += 1
                        self.update_counters()
                        self.can_output.insert(tk.END, f"TX: ID=0x{can_id:X}, Data={data.hex().upper()}\n", 'tx')
                        self.can_output.see(tk.END)

                except Exception as e:
                    self.error_count += 1
                    self.update_counters()
                    self.can_output.insert(tk.END, f"Error: {e}\n", 'error')
                    self.can_output.see(tk.END)

            time.sleep(TRANSMIT_INTERVAL)

    def start_transmission(self):
        global sending, send_thread

        if not db:
            messagebox.showerror("Error", "No DBC file loaded")
            return

        if not selected_ids:
            messagebox.showerror("Error", "No CAN IDs selected for transmission")
            return

        if sending:
            return

        sending = True
        self.status_var.set("Status: TRANSMITTING")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        send_thread = threading.Thread(target=self.transmit_loop, daemon=True)
        send_thread.start()

    def stop_transmission(self):
        global sending
        sending = False
        self.status_var.set("Status: IDLE")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def fetch_and_display_odometer(self):
        try:
            vin = self.vin_var.get().strip()
            if not vin:
                messagebox.showerror("Error", "Please enter a VIN number")
                return

            CA_CERT = r"D:\Cert\ca.pem"
            CLIENT_CERT = r"D:\Cert\cc.pem"
            CLIENT_KEY = r"D:\Cert\ck.pem"
            API_URL = f"https://aepltest.accoladeelectronics.com:8100/cvISOGenericCANProtobuf/getCvISOGenericCANProtobufDataWithTLS?topic=/device/{vin}/MQTTPROTOBUF/cvISOgenericCAN"

            response = requests.get(API_URL, cert=(CLIENT_CERT, CLIENT_KEY), verify=False)
            response.raise_for_status()
            json_data = response.json()

            self.api_output.delete(1.0, tk.END)
            self.api_output.insert(tk.END, f"API Response for VIN: {vin}\n\n", 'bold')
            self.api_output.insert(tk.END, json.dumps(json_data, indent=2))

        except requests.exceptions.RequestException as e:
            self.api_output.insert(tk.END, f"\n\nAPI Error: {e}", 'error')

    def validate_data(self):
        try:
            vin = self.vin_var.get().strip()
            if not vin:
                return

            if not selected_ids:
                return

            CA_CERT = r"D:\Cert\ca.pem"
            CLIENT_CERT = r"D:\Cert\cc.pem"
            CLIENT_KEY = r"D:\Cert\ck.pem"
            API_URL = f"https://aepltest.accoladeelectronics.com:8100/cvISOGenericCANProtobuf/getCvISOGenericCANProtobufDataWithTLS?topic=/device/{vin}/MQTTPROTOBUF/cvISOgenericCAN"

            # Clear previous results but keep header
            self.validate_output.delete(1.0, tk.END)
            self.validate_output.insert(tk.END, f"Auto-Validation Results for VIN: {vin}\n\n", 'bold')

            response = requests.get(API_URL, cert=(CLIENT_CERT, CLIENT_KEY), verify=False)
            response.raise_for_status()
            server_data = response.json()

            for can_id, signals in selected_ids.items():
                message = db.get_message_by_frame_id(can_id) if db else None
                if not message:
                    continue

                has_non_zero_signals = False
                signal_output = ""

                for signal_name, transmitted_value in signals.items():
                    if transmitted_value == 0 or transmitted_value == 0.0:
                        continue

                    signal = next((s for s in message.signals if s.name == signal_name), None)
                    if not signal:
                        continue

                    server_value = self.extract_server_value(server_data, can_id, signal_name)

                    signal_output += f"  {signal_name}:\n"
                    signal_output += f"    Transmitted: {transmitted_value}\n"
                    signal_output += f"    Server value: {server_value}\n"

                    tolerance = 0.01
                    if abs(transmitted_value - server_value) < tolerance:
                        signal_output += "    Status: MATCH\n\n"
                        has_non_zero_signals = True
                    else:
                        signal_output += "    Status: MISMATCH\n\n"
                        has_non_zero_signals = True

                if has_non_zero_signals:
                    self.validate_output.insert(tk.END, f"CAN ID: 0x{can_id:X}\n", 'bold')
                    self.validate_output.insert(tk.END, signal_output)

            # Add timestamp
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.validate_output.insert(tk.END, f"\nLast updated: {now}\n", 'timestamp')

        except requests.exceptions.RequestException as e:
            self.validate_output.insert(tk.END, f"\n\nAPI Error: {e}", 'error')

    def extract_server_value(self, server_data, can_id, signal_name):
        """
        Helper method to extract signal value from server response
        Modify this based on your actual API response structure
        """
        try:
            # Placeholder implementation - adapt to your API response format
            # This assumes server_data is a dictionary with messages containing signals
            messages = server_data.get('data', {}).get('messages', [])
            for msg in messages:
                if msg.get('can_id', 0) == can_id:
                    return msg.get('signals', {}).get(signal_name, 0)
            return 0
        except:
            return 0

    def start_telemetry_refresh(self):
        """Start automatic telemetry data refresh"""
        if not self.vin_var.get().strip():
            messagebox.showerror("Error", "Please enter a VIN number")
            return

        self.telemetry_refresh = True
        self.telemetry_start_btn.config(state=tk.DISABLED)
        self.telemetry_stop_btn.config(state=tk.NORMAL)

        # Clear previous data and start fresh
        self.telemetry_output.delete(1.0, tk.END)
        self.telemetry_packet_count = 0
        self.telemetry_count_label.config(text=f"Packets Received at Server: {self.telemetry_packet_count}")

        # Initialize last data tracking
        self.last_telemetry_data = None
        self.last_telemetry_timestamp = None

        # Start the telemetry thread
        self.telemetry_thread = threading.Thread(
            target=self.telemetry_refresh_loop,
            daemon=True
        )
        self.telemetry_thread.start()

    def stop_telemetry_refresh(self):
        """Stop automatic telemetry data refresh"""
        self.telemetry_refresh = False
        self.telemetry_start_btn.config(state=tk.NORMAL)
        self.telemetry_stop_btn.config(state=tk.DISABLED)

    def telemetry_refresh_loop(self):
        """Thread function for continuous telemetry data refresh"""
        last_packet_hash = None  # To track if we've seen this packet before

        while self.telemetry_refresh:
            try:
                vin = self.vin_var.get().strip()
                if not vin:
                    self.stop_telemetry_refresh()
                    return

                # Fetch telemetry data
                CA_CERT = r"D:\Cert\ca.pem"
                CLIENT_CERT = r"D:\Cert\cc.pem"
                CLIENT_KEY = r"D:\Cert\ck.pem"
                API_URL = f"https://aepltest.accoladeelectronics.com:8100/telemetryProtobuf/getTelemetryProtobufDataWithTLS?topic=/device/{vin}/MQTTPROTOBUF/telemetry"

                response = requests.get(API_URL, cert=(CLIENT_CERT, CLIENT_KEY), verify=False)
                response.raise_for_status()
                telemetry_data = response.json()

                # Create a hash of the packet data to detect new packets
                current_packet_hash = hash(json.dumps(telemetry_data, sort_keys=True))

                # Get current timestamp
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                # Check if this is a new packet (different from last received)
                if current_packet_hash != last_packet_hash:
                    # Update packet count only if data is different
                    self.telemetry_packet_count += 1
                    last_packet_hash = current_packet_hash

                    # Update UI in main thread with new packet flag
                    self.root.after(0, self.update_telemetry_display,
                                    telemetry_data, now, True)
                else:
                    # Just update the display without incrementing count
                    self.root.after(0, self.update_telemetry_display,
                                    telemetry_data, now, False)

                # Wait for next refresh
                time.sleep(API_REFRESH_INTERVAL)

            except requests.exceptions.RequestException as e:
                self.root.after(0, self.telemetry_output.insert, tk.END,
                                f"Error fetching telemetry data: {e}\n", 'error')
                time.sleep(API_REFRESH_INTERVAL)
            except Exception as e:
                self.root.after(0, self.telemetry_output.insert, tk.END,
                                f"Unexpected error: {e}\n", 'error')
                time.sleep(API_REFRESH_INTERVAL)

    def update_telemetry_display(self, telemetry_data, timestamp, is_new_packet):
        """Update the telemetry display with new data"""
        # Update packet count if this is a new packet
        if is_new_packet:
            self.telemetry_count_label.config(
                text=f"Packets Received at Server: {self.telemetry_packet_count}")

        # Insert timestamp and packet info
        self.telemetry_output.insert(tk.END, f"[{timestamp}] ", 'timestamp')

        if is_new_packet:
            self.telemetry_output.insert(tk.END,
                                         f"NEW Packet #{self.telemetry_packet_count}\n", 'count')
        else:
            self.telemetry_output.insert(tk.END,
                                         f"Same Packet (Last: #{self.telemetry_packet_count})\n", 'count')

        # Insert telemetry data with indentation
        self.telemetry_output.insert(tk.END, "Telemetry Data:\n")
        self.telemetry_output.insert(tk.END, json.dumps(telemetry_data, indent=2))
        self.telemetry_output.insert(tk.END, "\n\n")

        # Auto-scroll to bottom
        self.telemetry_output.see(tk.END)

    def on_close(self):
        """Handle window close event"""
        global sending
        sending = False
        self.telemetry_refresh = False
        self.auto_validate = False

        if send_thread and send_thread.is_alive():
            send_thread.join(1.0)

        if self.telemetry_thread and self.telemetry_thread.is_alive():
            self.telemetry_thread.join(1.0)

        if self.validate_thread and self.validate_thread.is_alive():
            self.validate_thread.join(0.1)

        self.transmitter.shutdown()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
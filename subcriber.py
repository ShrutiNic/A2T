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

        # ttk.Button(dbc_tab, text="Load DBC File", command=self.browse_dbc_file
        #            ).pack(fill=tk.X, pady=5)
        tk.Button(
            dbc_tab,
            text="Load DBC File",
            command=self.browse_dbc_file,
            bg="#2196F3",  # Blue background
            fg="Black",  # White text
            font=('Segoe UI', 10),
            relief=tk.FLAT  # Optional: Makes it look more modern
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

        # Control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=6)

        ttk.Button(btn_frame, text="Add", command=self.add_selected_id).pack(side=tk.LEFT, expand=True)
        ttk.Button(btn_frame, text="Remove", command=self.remove_selected_id).pack(side=tk.LEFT, expand=True)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_selected_ids).pack(side=tk.LEFT, expand=True)

       

        # self.start_btn = ttk.Button(control_frame, text="Start Transmission",
        #                             command=self.start_transmission, )

        self.start_btn = tk.Button(
            control_frame,
            text="Start Transmission",
            command=self.start_transmission,
            bg='green',
            fg='Black',
            font=('Segoe UI', 10)
        )
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=2)

        # self.stop_btn = ttk.Button(control_frame, text="Stop Transmission",
        #                            command=self.stop_transmission, style='Stop.TButton', state=tk.DISABLED)
        self.stop_btn = tk.Button(
            control_frame,
            text="Stop Transmission",
            command=self.stop_transmission,
            bg='Red',  # Background color
            fg='Black', # Text color (foreground)
            #state=tk.DISABLED,
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

        # Dashboard tab
        dashboard_tab = ttk.Frame(output_notebook)
        output_notebook.add(dashboard_tab, text="Dashboard")

        # Dashboard widgets would go here
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

        # Configure styles
        self.style.configure('Accent.TButton', foreground='white', background='#4CAF50')
        self.style.configure('Start.TButton', foreground='white', background='#2196F3')
        self.style.configure('Stop.TButton', foreground='white', background='#F44336')
        self.style.map('Accent.TButton', background=[('active', '#45a049')])
        self.style.map('Start.TButton', background=[('active', '#0b7dda')])
        self.style.map('Stop.TButton', background=[('active', '#d32f2f')])

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

    def clear_selected_ids(self):
        selected_ids.clear()
        self.update_selected_listbox()

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
                    print("OdoValDiag",odometer_tx_value)

                if self.auto_increment_speed.get() and 'VehSpdEMS' in signals:
                    signals['VehSpdEMS'] = speed_tx_value
                    speed_tx_value = (speed_tx_value + 1) % (VEHICLE_SPEED_MAX + 1)
                    print("VehSpdEMS",speed_tx_value)

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
                        self.tx_count_var.set(f"Messages Sent: {self.tx_count}")
                        self.can_output.insert(tk.END, f"TX: ID=0x{can_id:X}, Data={data.hex().upper()}\n", 'tx')
                        self.can_output.see(tk.END)

                except Exception as e:
                    self.error_count += 1
                    self.error_count_var.set(f"Errors: {self.error_count}")
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
            self.api_output.insert(tk.END, f"API Response for VIN: {vin}\n\n")
            self.api_output.insert(tk.END, json.dumps(json_data, indent=2))

            # Process the response as needed
            # ...

        except requests.exceptions.RequestException as e:
            self.api_output.insert(tk.END, f"\n\nAPI Error: {e}")

    def on_close(self):
        global sending
        sending = False

        if send_thread and send_thread.is_alive():
            send_thread.join(1.0)

        self.transmitter.shutdown()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


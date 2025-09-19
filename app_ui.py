'''
Copyright 2024-2025 Accolade Electronics Pvt. Ltd

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

file        app_ui.py
brief       This is the source file for the GUI constructs

date        22 March 2024
author      Accolade Electronics <www.accoladeelectronics.com>
'''

import sys     
import toml                     # for handling project information in TOML config (TOML is used as alternate to JSON)                
import tkinter as tk           
import pandas as pd 
from datetime import datetime
import time
from PIL import Image, ImageTk 
from tkinter import ttk, filedialog, messagebox, font
from tkinter import filedialog
import pandas as pd
import app_comm
import app_logic
import time
import threading
import cert_comm
import zlib
import os
import struct
import string

class AdditionalDialog(tk.Toplevel):
    def __init__(self, parent, requires):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.title("Additional Details")
        self.entries = {}
        for i, req in enumerate(requires):
            field_name = req["field"]
            default_value = req.get("default", "")
            max_length = req.get("max_length", 1000)
            print(f"app_ui    : {field_name} {default_value} {max_length}")
            
            tk.Label(self, text=field_name).grid(row=i, column=0, pady=5, padx=5)
            entry = tk.Entry(
                    self,
                    validate="key",
                    validatecommand=(
                        self.register(lambda x: len(x) <=max_length), 
                        "%P"
                    )
                )
            entry.grid(row=i, column=1, pady=5, padx=5)
            entry.insert(0, default_value)
            self.entries[field_name] = entry

        ok_button = tk.Button(self, text="OK", command=self.on_ok)
        ok_button.grid(row=len(requires), columnspan=2, pady=10, padx=5, sticky="ew")
        self.result = None
        
        self.center_window()
        self.wait_window(self)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def on_ok(self):
        self.result = {}
        for field_name, entry in self.entries.items():
            value = entry.get()
            if not value:
                messagebox.showwarning("Input Required", f"Please enter a value for {field_name}.")
                return
            self.result[field_name] = value
        self.destroy()

    def on_close(self):
        messagebox.showinfo("Input Required", "You must enter all required values to proceed.")

########################################### (GUI creation) ####################################################

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Accolade Service Tool')
        self.root.geometry('1200x640')  
        self.root.resizable(False, False)

        # Canvas for drawing grid
        # self.canvas = tk.Canvas(root, bg="white")
        # self.canvas.pack(fill="both", expand=True)
        
        # self.device_bg_image = tk.PhotoImage(file=self.get_resource_path('AccoladeBackground.png'))
        # self.canvas.create_image(0, 0, anchor='nw', image=self.device_bg_image)

        # # Label to display coordinates
        # self.coord_label = tk.Label(root, text="X: 0, Y: 0", font=("Arial", 10), bg="lightgray")
        # self.coord_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # # Draw grid
        # self.draw_grid()

        # # Track mouse motion
        # self.canvas.bind("<Motion>", self.update_mouse_coords)

        self.create_widgets()  
        
        super().__init__()
        self.dids_widgets = {} 
        self.dids_values = {}  
        self.dids_format = {}  
        self.dids_fired = False  
        self.selected_files_result = None
        self.g_project_combo_box
        self.g_project = None
        self.config_type = None
        self.buttons = {"CONNECT_BTN": self.connect_button}

    def draw_grid(self, spacing=20):
        w = self.canvas.winfo_reqwidth()
        h = self.canvas.winfo_reqheight()

        # Update after mainloop starts to get real size
        self.root.after(100, lambda: self._draw_grid_lines(spacing))

    def _draw_grid_lines(self, spacing):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        for i in range(0, w, spacing):
            self.canvas.create_line(i, 0, i, h, fill="#ddd")
        for i in range(0, h, spacing):
            self.canvas.create_line(0, i, w, i, fill="#ddd")

    def update_mouse_coords(self, event):
        self.coord_label.config(text=f"X: {event.x}, Y: {event.y}")

    def on_tab_change(self, event):
        current_tab = event.widget.tab(event.widget.select(), "text")
        if current_tab != "Device Setup":
            self.g_project_combo_box.place_forget()
        else:
            self.g_project_combo_box.place(x=550, y=438)
        
        if self.g_project_combo_box.current() ==0 and current_tab != "Device Setup":
            self.notebook.select(0)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.device_tab = tk.Frame(self.notebook)
        self.notebook.add(self.device_tab, text="Device Setup")

        self.config_tab = tk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Configuration")

        self.certificate_tab = tk.Frame(self.notebook)
        self.notebook.add(self.certificate_tab, text="Certificate")

        self.j1939_tab = tk.Frame(self.notebook)
        self.notebook.add(self.j1939_tab, text="J1939 Config")

        self.notebook.tab(1, state='disabled')  # Configuration
        self.notebook.tab(2, state='disabled')  # Certificate

        self.create_device_config_tab_widget()

        self.create_configuration_tab_widgets()

        self.create_certificate_tab_widgets()

        self.create_j1939_config_tab()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, relative_path)
            
        return os.path.join(os.path.abspath('.'), relative_path)
    

   
    def show_dialog(self, type, message):
        if type == 'Error':
            messagebox.showerror(type, message)
        elif type == 'Info':
            messagebox.showinfo(type, message)

    def on_project_selected(self, event):
        current = self.g_project_combo_box.current()
        self.g_project = g_config['projects'][current - 1]
        if current == 0:
            self.show_dialog('Error', 'Must choose a project')
            return
        print("app_ui    : selected", self.g_project_combo_box.get())
        print(self.g_project["name"], self.g_project["security"])
        self.notebook.tab(1, state='normal')  # Configuration
        self.notebook.tab(2, state='normal')  # Certificate
        self.g_project_combo_box.config(state='disabled')
    
    def create_labels(self):
        self.main_frame = tk.Frame(self.device_tab, padx=20, pady=20) 
        global g_config
        g_config = toml.load(open(self.get_resource_path('config.toml')))

        sw_label = tk.Label(self.root, text='v{}'.format(g_config['version']), font=('White Rabbit', 9), bg='white')
        sw_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        print('app_ui    : created labels')

    def create_combobox(self):
        projects = ['--Select Project--']
        for project in g_config['projects']:
            print(f"Loaded project name: {repr(project['name'])}")
            projects.append(project['name'])
    
        style = ttk.Style()
        style.theme_use('default')  # Use a theme that allows customization

        # Configure custom style for Combobox
        style.configure("Custom.TCombobox",
            font=('Fira Sans', 14),       # Larger font
            foreground="black",           # Text color
            background="lightblue",       # Background (doesn't affect dropdown on all platforms)
            fieldbackground="lightblue", # Inner box background
            padding=5
        )


        self.g_project_combo_box = ttk.Combobox(self.root, values=projects, width=25, state='readonly', style="Custom.TCombobox")
        self.g_project_combo_box.place(x=550, y=438)
        self.g_project_combo_box.current(0)

    print('app_ui    : created combobox')

    def create_device_config_tab_widget(self):
        # Use a canvas in the device tab to support background image
        self.device_canvas = tk.Canvas(self.device_tab, width=1200, height=640)
        self.device_canvas.pack(fill="both", expand=True)

        # Load image and keep reference
        self.device_bg_image = tk.PhotoImage(file=self.get_resource_path('AccoladeBackground.png'))
        self.device_canvas.create_image(0, 0, anchor='nw', image=self.device_bg_image)
        # self.device_canvas.create_window(100, 100, window=tk.Label(self.device_canvas, font=("Arial", 16)))

        self.img_normal = tk.PhotoImage(file="Button_Setup.png")
        self.img_id = self.device_canvas.create_image(600, 550, image=self.img_normal)
        self.device_canvas.tag_bind(self.img_id, "<Button-1>", self.on_project_selected)

        self.create_labels()
        self.create_combobox()

    def create_configuration_tab_widgets(self):
        self.main_frame = tk.Frame(self.config_tab, padx=10, pady=10)  # Reduced padding
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.upper_frame = tk.Frame(self.main_frame, height=160, width=1200, bg='sky blue')  
        self.upper_frame.pack(fill=tk.X)
        self.upper_frame.pack_propagate(False)  

        # Load logo
        if not hasattr(self, 'logo_photo'):  
            try:
                logo_image = Image.open("Accolade Logo Without Background 3.png")
                logo_image = logo_image.resize((250, 120), Image.LANCZOS)  # Reduced size
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                print("Logo loaded successfully for Configuration tab.")
            except Exception as e:
                print(f"Error loading logo: {e}")
                self.logo_photo = None

        if self.logo_photo:
            logo_label = tk.Label(self.upper_frame, image=self.logo_photo, bg='sky blue')
            logo_label.pack(side=tk.LEFT, padx=(10, 20))

        utility_name = tk.Label(self.upper_frame, text="CONFIGURATION", font=("Times New Roman", 25, "bold"), bg='sky blue')
        utility_name.place(x=460, y=50)  # Adjusted center

        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label = tk.Label(self.upper_frame, text=self.current_date, font=("Arial", 12), bg='sky blue')
        self.date_label.place(x=1050, y=50)  # Shifted left

        self.time_label = tk.Label(self.upper_frame, text="", font=("Arial", 12), bg='sky blue')
        self.time_label.place(x=1050, y=80)

        self.update_time()

        self.lower_frame = tk.Frame(self.main_frame)
        self.lower_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.lower_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 5))

        # Buttons layout
        button_spacing = 10
        self.load_button = tk.Button(button_frame, text="Load Excel File", command=self.load_excel)
        self.load_button.pack(side=tk.LEFT, padx=button_spacing)

        self.option_var = tk.StringVar(value="Select Config")
        self.dropdown = ttk.Combobox(button_frame, textvariable=self.option_var, state="readonly", width=20)
        self.dropdown.pack(side=tk.LEFT, padx=button_spacing)
        self.dropdown.bind("<<ComboboxSelected>>", self.display_selected_sheet)

        self.connect_button = tk.Button(button_frame, text="Connect to CAN Bus", command=lambda:app_logic.connect_to_can_bus(self.g_project))
        self.connect_button.pack(side=tk.LEFT, padx=button_spacing)

        self.config_button = tk.Button(button_frame, text="Config Reset", command=self.startConfig)
        self.config_button.pack(side=tk.LEFT, padx=button_spacing)

        self.read_button = tk.Button(button_frame, text="Read Config", command=self.fire_dids)
        self.read_button.pack(side=tk.LEFT, padx=button_spacing)

        self.write_button = tk.Button(button_frame, text="Write Config", command=self.write_dids)
        self.write_button.pack(side=tk.LEFT, padx=button_spacing)

        # Scrollable frame setup
        self.canvas = tk.Canvas(self.lower_frame, height=360)  # Fit in remaining area
        self.scrollbar = tk.Scrollbar(self.lower_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    

    def create_certificate_tab_widgets(self):
        self.main_frame = tk.Frame(self.certificate_tab, padx=20, pady=20)  
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.upper_frame = tk.Frame(self.main_frame, height=160, bg='sky blue')  
        self.upper_frame.pack(fill=tk.X)
        self.upper_frame.pack_propagate(False)  

        if not hasattr(self, 'logo_photo'):  
            try:
                logo_image = Image.open(r"Accolade Logo Without Background 3.png")  
                logo_image = logo_image.resize((300, 150), Image.LANCZOS)  
                self.logo_photo = ImageTk.PhotoImage(logo_image)  
                print("Logo loaded successfully for Certificate tab.")
            except Exception as e:
                print(f"Error loading logo: {e}")
                self.logo_photo = None

        if self.logo_photo:  
            logo_label = tk.Label(self.upper_frame, image=self.logo_photo, bg='sky blue')  
            logo_label.pack(side=tk.LEFT, padx=(10, 20))
        else:
            print("Logo not displayed in Certificate tab.")

        certificate_name = tk.Label(self.upper_frame, text="CERTIFICATE", font=("Times New Roman", 25, "bold"), bg='sky blue')  # Match background color
        certificate_name.place(x=530, y=50) 

        self.current_date = datetime.now().strftime("%Y-%m-%d") 
        self.date_label = tk.Label(self.upper_frame, text=self.current_date, font=("Arial", 14), bg='sky blue') 
        self.date_label.place(x=1150, y=60) 

        self.time_label = tk.Label(self.upper_frame, text="", font=("Arial", 14), bg='sky blue') 
        self.time_label.place(x=1150, y=90)  

        self.update_time()

        self.lower_frame = tk.Frame(self.main_frame, padx=20, pady=20)
        self.lower_frame.pack(fill=tk.BOTH, expand=True, pady=20)  

        self.select_button = tk.Button(self.lower_frame, text="Select 3 Files", command=self.select_files)
        self.select_button.pack(pady=10)

        self.file_label1 = tk.Label(self.lower_frame, text="No file selected", bg='sky blue')
        self.file_label1.pack(pady=5)

        self.file_label2 = tk.Label(self.lower_frame, text="No file selected", bg='sky blue')
        self.file_label2.pack(pady=5)

        self.file_label3 = tk.Label(self.lower_frame, text="No file selected", bg='sky blue')
        self.file_label3.pack(pady=5)

        #self.connect_button = tk.Button(self.lower_frame, text="Connect to CAN Bus", command= app_logic.connect_to_can_bus(self.g_project) )
        self.connect_button = tk.Button(self.lower_frame, text="Connect to CAN Bus", command=lambda: app_logic.connect_can(self.g_project))
        self.connect_button.pack(side=tk.LEFT, padx=50)  

        self.security_button = tk.Button(self.lower_frame, text="Start Download", command=self.startCertRoutine)
        self.security_button.pack(side=tk.LEFT, padx=50)
        

    def create_j1939_config_tab(self):
        self.j1939_ids = []
        self.selected_ids = []

        upload_btn = tk.Button(self.j1939_tab, text="Upload J1939 Config File", command=self.load_j1939_excel)
        upload_btn.pack(pady=10)

        frame = tk.Frame(self.j1939_tab)
        frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Listbox for all CAN IDs
        tk.Label(frame, text="Available CAN IDs").grid(row=0, column=0)
        left_frame = tk.Frame(frame)
        left_frame.grid(row=1, column=0, padx=10, sticky='nsew')
        self.j1939_listbox = tk.Listbox(left_frame, width=30, height=15)
        scroll_y_left = tk.Scrollbar(left_frame, orient="vertical", command=self.j1939_listbox.yview)
        self.j1939_listbox.configure(yscrollcommand=scroll_y_left.set)
        self.j1939_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y_left.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=1, column=1)
        tk.Button(btn_frame, text="Add →", command=self.add_j1939_id).pack(pady=5)
        tk.Button(btn_frame, text="← Remove", command=self.remove_j1939_id).pack(pady=5)

        # Listbox for selected IDs
        tk.Label(frame, text="Selected for UDS Config").grid(row=0, column=2)
        self.selected_listbox = tk.Listbox(frame, width=30, height=15)
        self.selected_listbox.grid(row=1, column=2, padx=10)

        # Bottom buttons
        bottom_btns = tk.Frame(self.j1939_tab)
        bottom_btns.pack(pady=10)

        #tk.Button(bottom_btns, text="Send via UDS", command=self.send_selected_ids).pack(side=tk.LEFT, padx=10)
        #tk.Button(bottom_btns, text="Update", command=self.update_selected_ids).pack(side=tk.LEFT, padx=10)

    def load_j1939_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            self.j1939_ids = df.iloc[:, 0].dropna().astype(str).tolist()
            self.j1939_listbox.delete(0, tk.END)
            for cid in self.j1939_ids:
                self.j1939_listbox.insert(tk.END, cid)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel: {e}")

    def add_j1939_id(self):
        selection = self.j1939_listbox.curselection()
        for index in selection:
            value = self.j1939_listbox.get(index)
            if value not in self.selected_ids:
                self.selected_ids.append(value)
                self.selected_listbox.insert(tk.END, value)

    def remove_j1939_id(self):
        selection = self.selected_listbox.curselection()
        for index in reversed(selection):
            value = self.selected_listbox.get(index)
            self.selected_ids.remove(value)
            self.selected_listbox.delete(index)

    # def send_selected_ids(self):
    #     if not self.selected_ids:
    #         messagebox.showinfo("Info", "No CAN IDs selected.")
    #         return
    #     # Send logic here (currently mocked)
    #     message_bytes = bytearray()
    #     count = len(self.selected_ids)
    #     message_bytes.append(count)
    #     print("[UDS] Sending selected CAN IDs over UDS:")
    #     for can_id in self.selected_ids:
    #         print(" →", can_id)

    #         # Construct 4-byte PGN with MSB = 0x00
    #         message_bytes.append((int(can_id, 16) >> 24) &  0xFF)           # MSB padding
    #         message_bytes.append((int(can_id, 16) >> 16) & 0xFF)             # PGN high byte
    #         message_bytes.append((int(can_id, 16) >> 8) & 0xFF)             # PGN low byte
    #         message_bytes.append(int(can_id,16) & 0xFF)           # Reserved/padding (optional)
            
    #     try:
    #         import app_comm  
    #         response_data, is_valid = app_comm.startRoutine(self.g_project["security"]) 
    #         if not is_valid or response_data['type'] != 'Positive':
    #             print(f"StartRoutine failed with response: {response_data['type'] if response_data else 'None'}")
    #             messagebox.showerror("Error", f"Routine start failed: {response_data['type'] if response_data else 'Unknown error'}")
    #             return 
    #         response_data = app_comm.test_pgn_config_did(0x5522, message_bytes)
    #         print("Response data in UI: ", response_data)
    #         print(f"Calling test_pgn_config_did for DID {0x522} with hex value {message_bytes}")
    #     finally:
    #             self.write_button.config(state='normal')
    
    def update_selected_ids(self):
        if not self.selected_ids:
            messagebox.showinfo("Info", "No CAN IDs selected.")
            return

        # Example logic for updating selected CAN IDs
        message_bytes = bytearray()
        count = len(self.selected_ids)
        message_bytes.append(count)
        print("[UPDATE] Updating selected CAN IDs:")
        
        for can_id in self.selected_ids:
            print(" →", can_id)

            # Similar 4-byte construction
            message_bytes.append((int(can_id, 16) >> 24) & 0xFF)
            message_bytes.append((int(can_id, 16) >> 16) & 0xFF)
            message_bytes.append((int(can_id, 16) >> 8) & 0xFF)
            message_bytes.append(int(can_id, 16) & 0xFF)

        try:
            import app_comm
            response_data, is_valid = app_comm.startRoutine(self.g_project["security"])
            if not is_valid or response_data['type'] != 'Positive':
                print(f"StartRoutine failed with response: {response_data['type'] if response_data else 'None'}")
                messagebox.showerror("Error", f"Routine start failed: {response_data['type'] if response_data else 'Unknown error'}")
                return

            # Assuming different DID or command for update
            response_data = app_comm.test_pgn_config_did(0x5523, message_bytes)  # Different DID from send
            print("Response data in UI (update):", response_data)
            print(f"Calling test_pgn_config_did for DID {hex(0x5523)} with hex value {message_bytes}")

        finally:
            self.write_button.config(state='normal')
    
    def set_btn_enabled(self, btn_name, is_enabled):
        if btn_name in self.buttons:
            state = 'normal' if is_enabled else 'disabled'
            self.buttons[btn_name].config(state=state)
        else:
            print(f"Button '{btn_name}' not found.")
        
    def update_selected_ids(self):
            print("[UPDATE] Final Configured CAN IDs:")
            for cid in self.selected_ids:
                print(" -", cid)    

    def crc32_calc(self, running_crc, data):
        """Calculates CRC32 for the given data."""
        POLYNOMIAL = 0x04C11DB7
        for byte in data:
            running_crc ^= (byte << 24) 
            for _ in range(8):
                msb = running_crc >> 31  
                running_crc = (running_crc << 1) & 0xFFFFFFFF 
                running_crc ^= (0 - msb) & POLYNOMIAL
        return running_crc

    def get_file_crc(self, file_path, buffer_size=4096):
        """Calculates the CRC32 of a file."""
        running_crc = 0xFFFFFFFF  

        with open(file_path, "rb") as file:
            while (data := file.read(buffer_size)):
                running_crc = self.crc32_calc(running_crc, data)

        running_crc = running_crc & 0xFFFFFFFF 
        return running_crc
    
    def crc16_calc(self, running_crc, data):
        """Calculates CRC16 for the given data using CRC-16-IBM (no lookup table)."""
        print("Crc16 calc is called...")
        POLYNOMIAL = 0x04C11DB7
        for byte in data:
            running_crc ^= (byte << 8)  # Align byte to high-order bits of 16-bit CRC
            for _ in range(8):
                if running_crc & 0x8000:
                    running_crc = ((running_crc << 1) ^ POLYNOMIAL) & 0xFFFF
                else:
                    running_crc = (running_crc << 1) & 0xFFFF
        print("Running crc", running_crc)
        return running_crc
    
    def get_file_crc16(self, file_path, buffer_size=4096):
        """Calculates the CRC16 of a file."""
        running_crc = 0xFFFF

        with open(file_path, "rb") as file:
            while (data := file.read(buffer_size)):
                running_crc = self.crc16_calc(running_crc, data)

        return running_crc  # No final XOR needed for CRC-16-IBM


    # def select_files(self):
    #     """Handles file selection and data preparation."""
    #     file_paths = filedialog.askopenfilenames(filetypes=[("PEM Files", "*.pem")])

    #     if file_paths:
    #         selected_files = file_paths[:3]  
    #         file_sequence_mapping = {'ca.pem': '0x01', 'cc.pem': '0x02', 'ck.pem': '0x03'}
    #         categorized_files = []
    #         file_01_data = None

    #         for file_path in selected_files:
    #             file_name = os.path.basename(file_path).lower()
    #             if file_name in file_sequence_mapping:
    #                 sequence_number = file_sequence_mapping[file_name]
    #                 #crc32_value = self.get_file_crc(file_path)
    #                 crc16_value = self.get_file_crc16(file_path)
    #                 #crc32_hex = format(crc32_value, '08X')
    #                 crc16_hex = format(crc16_value, '08X')
    #                 file_size = os.path.getsize(file_path)

    #                 file_size_hex = f"0x{file_size:08X}"

    #                 file_data = {
    #                     "file_name": file_name,
    #                     "sequence_number": sequence_number,
    #                     "file_path": file_path,
    #                     #"crc32": crc32_hex,
    #                     "crc16":crc16_hex,
    #                     "file_size": file_size_hex 
    #                 }

    #                 categorized_files.append(file_data)

    #                 if sequence_number == '0x01':
    #                     file_01_data = file_data

    #                 label_text = (
    #                     f"{file_name.upper()}\n"
    #                     f"Sequence: {sequence_number}\n"
    #                     #f"CRC32: {crc32_hex}\n"
    #                     f"CRC16: {crc16_hex}\n"
    #                     f"Size: {file_size_hex} (hex)"
    #                 )
    #                 if sequence_number == '0x01':
    #                     self.file_label1.config(text=label_text)
    #                 elif sequence_number == '0x02':
    #                     self.file_label2.config(text=label_text)
    #                 elif sequence_number == '0x03':
    #                     self.file_label3.config(text=label_text)

    #         if not file_01_data:
    #             print("Error: File with sequence number 0x01 is missing!")
    #             self.selected_files_result = None
    #             return

    #         categorized_files.sort(key=lambda x: int(x['sequence_number'], 16))

    #         sorted_file_sizes = [file_data["file_size"] for file_data in categorized_files]

    #         self.selected_files_result = {
    #             "file_01_data": file_01_data,
    #             "all_files_data": categorized_files,
    #             "sorted_file_sizes": sorted_file_sizes  
    #         }

    #         print("Files selected and data prepared in correct order.")
    #         return self.selected_files_result

    #     else:
    #         print("No files selected.")
    #         self.selected_files_result = None

    def select_files(self):
        """Handles single file selection and data preparation."""
        file_path = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem")])

        if file_path:
            file_name = os.path.basename(file_path).lower()
            file_sequence_mapping = {'ca.pem': '0x01', 'cc.pem': '0x02', 'ck.pem': '0x03'}
            
            if file_name in file_sequence_mapping:
                sequence_number = file_sequence_mapping[file_name]
                crc16_value = self.get_file_crc16(file_path)
                crc16_hex = format(crc16_value, '08X')
                file_size = os.path.getsize(file_path)
                file_size_hex = f"0x{file_size:08X}"

                file_data = {
                    "file_name": file_name,
                    "sequence_number": sequence_number,
                    "file_path": file_path,
                    "crc16": crc16_hex,
                    "file_size": file_size_hex
                }

                label_text = (
                    f"{file_name.upper()}\n"
                    f"Sequence: {sequence_number}\n"
                    f"CRC16: {crc16_hex}\n"
                    f"Size: {file_size_hex} (hex)"
                )
                if sequence_number == '0x01':
                    self.file_label1.config(text=label_text)
                elif sequence_number == '0x02':
                    self.file_label2.config(text=label_text)
                elif sequence_number == '0x03':
                    self.file_label3.config(text=label_text)

                self.selected_files_result = file_data
                print("File selected and data prepared.")
                return self.selected_files_result
            else:
                print(f"Error: Selected file '{file_name}' is not recognized in the sequence mapping.")
                self.selected_files_result = None
                return None
        else:
            print("No file selected.")
            self.selected_files_result = None

    


    # def startCertRoutine(self):
    #         """Handles some method where you want to trigger the startRoutine."""
    #         if not self.selected_files_result:
    #             print("Error: No files selected. Please select files first.")
    #             return 

    #         response_data, is_valid = app_comm.startRoutineCert(self.selected_files_result)
            
    #         if not is_valid or response_data['type'] != 'Positive':
    #             print(f"StartRoutine failed with response: {response_data['type'] if response_data else 'None'}")
    #             messagebox.showerror("Error", f"Routine start failed: {response_data['type'] if response_data else 'Unknown error'}")
    #             return  
    
    def startCertRoutine(self):
        """Handles triggering the startRoutine for single or multiple files."""

        # Check if any files are selected
        if not self.selected_files_result:
            print("Error: No files selected. Please select files first.")
            return

        # Ensure selected_files_result is always a list
        if not isinstance(self.selected_files_result, list):
            self.selected_files_result = [self.selected_files_result]

        # Wrap files in dict with expected key
        files_dict = {"all_files_data": self.selected_files_result}

        try:
            is_valid, response_data = app_comm.startRoutineCert(files_dict)
        except Exception as e:
            print(f"Exception during startRoutineCert: {e}")
            messagebox.showerror("Error", f"Exception during routine start: {e}")
            return

        # Validate the response_data structure and status
        if not is_valid:
            print(f"StartRoutine failed: is_valid={is_valid}")
            messagebox.showerror("Error", f"Routine start failed: is_valid={is_valid}")
            return

        if isinstance(response_data, dict):
            if response_data.get('type') != 'Positive':
                print(f"StartRoutine failed with response type: {response_data.get('type')}")
                messagebox.showerror("Error", f"Routine start failed: {response_data.get('type')}")
                return
        elif isinstance(response_data, bool):
            if not response_data:
                print("StartRoutine failed: response_data is False")
                messagebox.showerror("Error", "Routine start failed: response_data is False")
                return
            # If True, treat as success
        else:
            print(f"Unexpected response_data type: {type(response_data)}")
            messagebox.showerror("Error", f"Routine start failed: Unexpected response type")
            return

        # Success case (optional feedback)
        print("Routine started successfully!")




    
    def clear_display(self):
        self.option_var.set('')  
        self.dropdown.set('Select Config')  
        self.dropdown['values'] = []  

        self.df = None  
        self.sheet_names = []  
        self.display_parameters = None  

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entry_widgets = []  
        self.dids = []  
        self.check_vars = []  
        self.dids_values = {}  
        self.dids_format = [] 
        self.selected_dids = {} 
            
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")  
        self.time_label.config(text=current_time)  
        self.time_label.after(1000, self.update_time) 

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if not file_path:
            return

        try:
            print(file_path)
            self.df = pd.ExcelFile(file_path)
            self.sheet_names = self.df.sheet_names
            self.dropdown['values'] = self.sheet_names
            self.option_var.set(self.sheet_names[0])  
            self.display_parameters(self.sheet_names[0])

            messagebox.showinfo("Excel Loaded", f"Excel file loaded successfully with sheets: {', '.join(self.sheet_names)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {e}")


    def display_selected_sheet(self, event):
        if self.df is None:
            messagebox.showerror("Error", "No Excel file loaded. Please load a file first.")
            return

        selected_sheet = self.option_var.get()  
        if selected_sheet not in self.sheet_names:
            messagebox.showerror("Error", f"Sheet '{selected_sheet}' not found. Please select a valid sheet.")
            return

        config_type_mapping = {
            'tmlConfig': '0x01',
            'aeplConfig': '0x02',
            'sysConfig': '0x03',
            'ais140Config': '0x04'
        }

        if selected_sheet in config_type_mapping:
            config_type = config_type_mapping[selected_sheet]
            print(f"Config Type for selected sheet '{selected_sheet}': {config_type}")
            self.config_type = config_type 
        
        self.display_parameters(selected_sheet)

    def display_parameters(self, selected_sheet):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            df_sheet = self.df.parse(selected_sheet)
            self.parameters = df_sheet[['UDS Parameter', 'DID', 'Parameter Access', 'FORMAT', 'Range', 'Data Type']].values.tolist()
            
            self.entry_widgets = []
            self.dids = []
            self.check_vars = []
            self.dids_values = {}
            self.dids_format = []
            self.selected_dids = {}

            num_columns = 2  # fixed to 2 columns to avoid horizontal scroll
            for idx, (param, did, access, format_type, did_range, data_type) in enumerate(self.parameters):
                col = idx % 2
                row = idx // 2

                check_var = tk.BooleanVar()
                self.check_vars.append(check_var)
                if did_range == 'nan':
                    continue
                # Create a frame to hold each entry group
                group_frame = tk.Frame(self.scrollable_frame, bd=1, relief='solid', bg='#f5f5f5', padx=4, pady=2)
                group_frame.grid(row=row, column=col * 2, padx=20, pady=5, sticky='nw')  # spacing between two columns

                checkbox_state = 'disabled' if access == "Read" else 'normal'
                checkbox = tk.Checkbutton(group_frame, variable=check_var, state=checkbox_state, bg='#f5f5f5')
                checkbox.grid(row=0, column=0, padx=(0, 5))

                param_label = tk.Label(group_frame, text=param, width=18, anchor='w', bg='#f5f5f5')
                param_label.grid(row=0, column=1, padx=5)

                did_label = tk.Label(group_frame, text=did, width=10, anchor='w', bg='#f5f5f5')
                did_label.grid(row=0, column=2, padx=5)

                text_box = tk.Entry(group_frame, width=20)
                if access == "Read":
                    text_box.config(state='disabled', background='lightgray')
                else:
                    text_box.config(state='normal', background='white')
                text_box.grid(row=0, column=3, padx=5)

                text_box.bind('<Key>', lambda event, entry=text_box: entry.config(fg='green'))

                self.dids_format.append(format_type.upper())
                self.dids_values[did] = {'widget': text_box, 'format': format_type.upper(), 'range': did_range, 'data_type': data_type}
                print("did, range", did, did_range)
                checkbox.config(command=lambda did=did, text_box=text_box, check_var=check_var: self.store_did_value(did, text_box, check_var))

                try:
                    if isinstance(did, str) and did.strip():
                        did_value = int(did.strip(), 16)
                        self.dids.append(did_value)
                        self.entry_widgets.append((did_value, text_box, check_var))
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid DID format: {did}. Skipping.\n\n{e}")

            for col in range(num_columns * 4):  # total used columns
                self.scrollable_frame.grid_columnconfigure(col, weight=1)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to display parameters: {e}")

    

    # def store_did_value(self, did, text_box, check_var):
    #     if check_var.get(): 
    #         value = text_box.get()  
    #         if value.strip():  
    #             did_info = self.dids_values.get(did)  
    #             if did_info:
    #                 did_format = did_info['format']  
    #                 did_range = did_info.get('range', None)  
    #                 data_type = did_info.get('data_type', None) 

    #                 if did_format == "DECIMAL":
    #                     try:
    #                         decimal_value = int(value)  
                            
    #                         if did_range:
    #                             try:
    #                                 min_range, max_range = map(int, did_range.strip('()').split(','))
    #                                 if decimal_value < min_range or decimal_value > max_range:
    #                                     messagebox.showerror("Error", f"Value for DID {did} is out of range. Must be between {min_range} and {max_range}")
    #                                     return
    #                             except ValueError:
    #                                 messagebox.showerror("Error", f"Invalid range format for DID {did}. Expected format: (min, max)")
    #                                 return
                            
    #                         hex_value = format(decimal_value, 'X').upper()

    #                         if data_type == "uint16_t":
    #                             if len(hex_value) == 2:  
    #                                 hex_value = '00' + hex_value  

    #                         self.selected_dids[did] = hex_value  
    #                         print(f"Stored DID: {did}, Value (Decimal to Hex): {hex_value}")
    #                     except ValueError as e:
    #                         messagebox.showerror("Error", f"Invalid decimal value for DID {did}: {e}")

    #                 elif did_format == "ASCII STRING":
    #                     try:
    #                         ascii_bytes = value.encode('ascii')  
                            
    #                         if did_range:
    #                             try:
    #                                 min_range, max_range = map(int, did_range.strip('()').split(','))
    #                                 if len(ascii_bytes) < min_range or len(ascii_bytes) > max_range:
    #                                     messagebox.showerror("Error", f"Invalid length for ASCII value of DID {did}. Length must be between {min_range} and {max_range}.")
    #                                     return
    #                             except ValueError:
    #                                 messagebox.showerror("Error", f"Invalid range format for DID {did}. Expected format: (min, max)")
    #                                 return
                            
    #                         ascii_hex = ''.join(format(byte, '02x') for byte in ascii_bytes)  
    #                         self.selected_dids[did] = ascii_hex  
    #                         print(f"Stored DID: {did}, Value (ASCII to Hex): {ascii_hex}")
    #                     except (UnicodeEncodeError, ValueError) as e:
    #                         messagebox.showerror("Error", f"Invalid ASCII value for DID {did}: {e}")

    #                 else:
    #                     messagebox.showerror("Error", f"Unknown format for DID {did}: {did_format}")
    #             else:
    #                 messagebox.showerror("Error", f"No information found for DID {did}.")
    #         else:
    #             if did in self.selected_dids:
    #                 del self.selected_dids[did]
    #             print(f"Removed DID: {did} due to empty value.")  
    #     else:
    #         if did in self.selected_dids:
    #             del self.selected_dids[did]
    #         print(f"Unchecked DID: {did} and removed it.")  
    
    

    def store_did_value(self, did, text_box, check_var):
        #print(f"[DEBUG] store_did_value called for DID=0x{did:X}, check={check_var.get()}, input='{text_box.get()}'")

        # Always remove if unchecked
        if not check_var.get():
            self.selected_dids.pop(did, None)
            #print(f"[DEBUG] DID 0x{did:X}: Checkbox unchecked → removed")
            return

        raw = text_box.get()
        special = {0x552B, 0x552C, 0x5513, 0xF1EF}

        # If empty but special DID, use placeholder
        if not raw.strip() and did in special:
            placeholder = "(null)" if did == 0xF1EF else "(empty)"
            self.selected_dids[did] = placeholder
            print(f"[DEBUG] DID 0x{did:X} (special): Empty input → placeholder '{placeholder}'")
            return
        elif not raw.strip():
            self.selected_dids.pop(did, None)
            print(f"[DEBUG] DID 0x{did:X}: Empty input → removed")
            return

        # Process ASCII data
        ascii_string = raw.encode('latin1', errors='ignore').decode('ascii', errors='ignore')
        # Filter only printable characters
        filtered = ''.join(c for c in ascii_string if c in string.printable)

        # Replace empty or non-displayable strings for special DIDs
        if not filtered and did in special:
            filtered = "(null)" if did == 0xF1EF else "(empty)"

        self.selected_dids[did] = filtered
        #print(f"[DEBUG] DID 0x{did:X}: Stored display='{filtered}'")


    
    
    def write_dids(self):
        if not self.selected_dids:
            messagebox.showwarning("Warning", "No DIDs selected or values entered.")
            return
        
        def write_dids_loop():
            self.write_button.config(state='disabled')  

            try:
                # import app_comm  
                # response_data, is_valid = app_comm.startRoutine(self.g_project)  

                # if not is_valid or response_data['type'] != 'Positive':
                #     print(f"StartRoutine failed with response: {response_data['type'] if response_data else 'None'}")
                #     messagebox.showerror("Error", f"Routine start failed: {response_data['type'] if response_data else 'Unknown error'}")
                #     return  

                for did, hex_value in self.selected_dids.items():
                    try:
                        response_data = app_comm.test_write_did(did, hex_value)
                        print("Response data in UI: ", response_data)
                        print(f"Calling test_write_did for DID {did} with hex value {hex_value}")

                        if response_data.get("type") == "Negative":
                            error_message = response_data.get("error", "Negative response")
                            messagebox.showerror("Error", f"Failed to write DID {did} with hex value {hex_value}: {error_message}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error writing DID {did}: {e}")
                        messagebox.showerror("Error", f"Error writing DID {did}: {e}")

                messagebox.showinfo("Complete",f"The DID writing is complete !")
            finally:
                self.write_button.config(state='normal')

        threading.Thread(target=write_dids_loop, daemon=True).start()


    

    # def fire_dids(self):
    #     if not self.dids:
    #         messagebox.showwarning("No DIDs", "No DIDs loaded. Please load an Excel file first.")
    #         return
    #
    #     self.clear_all_text_boxes()
    #
    #     def safe_update_did_widget(did, value):
    #         print("safe_update_did_widget", did)
    #         self.root.after(0, lambda: self.update_did_widget(did, value))
    #
    #     def fire_dids_loop():
    #         self.read_button.config(state='disabled')
    #
    #         import app_comm
    #
    #         # Start routine if required
    #         if self.g_project["name"] == "ATCU - 29 bit":
    #             response_data, is_valid = app_comm.startRoutine(self.g_project)
    #             if not is_valid or response_data.get('type') != 'Positive':
    #                 print(f"StartRoutine failed with response: {response_data.get('type', 'None')}")
    #                 messagebox.showerror("Error", f"Routine start failed: {response_data.get('type', 'Unknown error')}")
    #                 self.read_button.config(state='normal')
    #                 return
    #
    #         dids_to_fire = self.dids[:]
    #
    #         for index, did in enumerate(dids_to_fire):
    #             try:
    #                 print(f"\n--- Reading DID {hex(did)} (Index {index}) ---")
    #                 response = app_comm.test_read_write_did(
    #                     app_comm.g_pcan_handle,
    #                     app_comm.g_pcan_config,
    #                     did,
    #                     safe_update_did_widget  # Use safe update method
    #                 )
    #
    #                 if response:
    #                     # Convert list to string if needed
    #                     if isinstance(response, list):
    #                         response = "".join(response)
    #
    #                     print(f"Raw Response for DID {hex(did)}: {response}")
    #
    #                     format_type = self.dids_format[index]
    #                     print(f"Expected Format: {format_type}")
    #
    #                     # Hex string check
    #                     if isinstance(response, str) and all(c in "0123456789abcdefABCDEF" for c in response.strip()):
    #                         if format_type == 'DECIMAL':
    #                             try:
    #                                 # decimal_value = int(response, 16)
    #                                 # print(f"Converted to Decimal: {decimal_value}")
    #                                 safe_update_did_widget(did, response.lstrip('0'))
    #                             except ValueError:
    #                                 print(f"Decimal conversion failed for DID {hex(did)}: {response}")
    #                         elif format_type == 'ASCII STRING':
    #                             try:
    #                                 ascii_value = bytes.fromhex(response).decode('utf-8')
    #                                 print(f"Converted to ASCII: {ascii_value}")
    #                                 safe_update_did_widget(did, ascii_value)
    #                             except (ValueError, UnicodeDecodeError) as e:
    #                                 print(f"UTF-8 decode failed: {e}, trying ASCII with 'ignore'")
    #                                 ascii_value = bytes.fromhex(response).decode('ascii', errors='ignore')
    #                                 print(f"Decoded (fallback): {ascii_value}")
    #                                 safe_update_did_widget(did, ascii_value)
    #                         else:
    #                             print(f"Unknown format type: {format_type}")
    #                     else:
    #                         print(f"Invalid hex string: {response}")
    #                 else:
    #                     print(f"No response received for DID {hex(did)}")
    #
    #             except Exception as e:
    #                 print(f"Exception reading DID {hex(did)}: {e}")
    #
    #             time.sleep(0.3)  # Increased sleep for stability
    #
    #         self.read_button.config(state='normal')
    #         messagebox.showinfo("Success", "All DIDs read successfully.")
    #
    #     threading.Thread(target=fire_dids_loop, daemon=True).start()

    def fire_dids(self):
        if not self.dids:
            messagebox.showwarning("No DIDs", "No DIDs loaded. Please load an Excel file first.")
            return

        self.clear_all_text_boxes()

        def safe_update_did_widget(did, value):
            print("safe_update_did_widget", did)
            self.root.after(0, lambda: self.update_did_widget(did, value))

        def fire_dids_loop():
            self.read_button.config(state='disabled')

            import app_comm

            # Start routine if required
            if self.g_project["name"] == "ATCU - 29 bit":
                response_data, is_valid = app_comm.startRoutine(self.g_project)
                if not is_valid or response_data.get('type') != 'Positive':
                    print(f"StartRoutine failed with response: {response_data.get('type', 'None')}")
                    messagebox.showerror("Error", f"Routine start failed: {response_data.get('type', 'Unknown error')}")
                    self.read_button.config(state='normal')
                    return

            dids_to_fire = self.dids[:]

            for index, did in enumerate(dids_to_fire):
                try:
                    print(f"\n--- Reading DID {hex(did)} (Index {index}) ---")
                    response = app_comm.test_read_write_did(
                        app_comm.g_pcan_handle,
                        app_comm.g_pcan_config,
                        did,
                        safe_update_did_widget  # Use safe update method
                    )

                    if response:
                        # Convert list to string if needed
                        if isinstance(response, list):
                            response = "".join(response)

                        print(f"Raw Response for DID {hex(did)}: {response}")

                        format_type = self.dids_format[index]
                        print(f"Expected Format: {format_type}")

                        # Hex string check
                        if isinstance(response, str) and all(c in "0123456789abcdefABCDEF" for c in response.strip()):
                            if format_type == 'DECIMAL':
                                try:
                                    decimal_value = int(response, 16)  # Convert hex to decimal
                                    print(f"Converted to Decimal: {decimal_value}")
                                    safe_update_did_widget(did, str(decimal_value))
                                except ValueError:
                                    print(f"Decimal conversion failed for DID {hex(did)}: {response}")
                            elif format_type == 'ASCII STRING':
                                try:
                                    ascii_value = bytes.fromhex(response).decode('utf-8')
                                    print(f"Converted to ASCII: {ascii_value}")
                                    safe_update_did_widget(did, ascii_value)
                                except (ValueError, UnicodeDecodeError) as e:
                                    print(f"UTF-8 decode failed: {e}, trying ASCII with 'ignore'")
                                    ascii_value = bytes.fromhex(response).decode('ascii', errors='ignore')
                                    print(f"Decoded (fallback): {ascii_value}")
                                    safe_update_did_widget(did, ascii_value)
                            else:
                                print(f"Unknown format type: {format_type}")
                        else:
                            print(f"Invalid hex string: {response}")
                    else:
                        print(f"No response received for DID {hex(did)}")

                except Exception as e:
                    print(f"Exception reading DID {hex(did)}: {e}")

                time.sleep(0.3)  # Increased sleep for stability

            self.read_button.config(state='normal')
            messagebox.showinfo("Success", "All DIDs read successfully.")

        threading.Thread(target=fire_dids_loop, daemon=True).start()

    def normalize_did_key(self, did):
        if isinstance(did, int):
            return "0x" + format(did, '04X')
        elif isinstance(did, str):
            did = did.strip().upper()
            if not did.startswith("0X"):
                did = "0x" + did
            return did
        else:
            raise ValueError(f"Invalid DID format: {did}")

    def update_did_widget(self, did, hex_data):
        try:
            did_key = self.normalize_did_key(did)
            print(f"[DEBUG] Normalized DID key: {did_key}, {did}")
            print(f"[DEBUG] Available DID keys: {list(self.dids_values.keys())}")

            if did_key in self.dids_values:
                did_info = self.dids_values[did_key]
                text_box = did_info.get('widget')
                if text_box:
                    state = text_box.cget('state')
                    if state == 'disabled':
                        text_box.config(state='normal')

                    # Prepare display string
                    if isinstance(hex_data, list):
                        display_data = ''.join(hex_data)

                    else:
                        display_data = str(hex_data)

                    text_box.delete(0, tk.END)
                    text_box.insert(0, display_data)

                    if state == 'disabled':
                        text_box.config(state='disabled')
                    print(f"[INFO] Updated widget for DID {did_key} with data: {display_data}")
                else:
                    print(f"[WARNING] Text box widget missing for DID {did_key}")
            else:
                print(f"[WARNING] DID {did_key} not found in dids_values.")
        except Exception as e:
            print(f"[ERROR] Exception updating widget for DID {did}: {e}")
            import traceback
            traceback.print_exc()



    def startConfig(self):
        print("start config called", self.config_type)
        if self.config_type == '0x01':
            response_data, is_valid= app_comm.startRoutineConfig(self.g_project["security"])
            if not is_valid or response_data['type'] != 'Positive':
                    print(f"Stop Routine failed with response: {response_data['type'] if response_data else 'None'}")
                    messagebox.showerror("Error", f"Routine Stop failed: {response_data['type'] if response_data else 'Unknown error'}")
                    return 
        elif self.config_type == '0x02':
            response_data, is_valid= app_comm.startRoutineConfig_aepl(self.g_project["security"])
            if not is_valid or response_data['type'] != 'Positive':
                    print(f"Stop Routine failed with response: {response_data['type'] if response_data else 'None'}")
                    messagebox.showerror("Error", f"Routine Stop failed: {response_data['type'] if response_data else 'Unknown error'}")
                    return   
         

    def clear_all_text_boxes(self):
        try:
            for did_key, did_info in self.dids_values.items():
                text_box = did_info.get('widget')  
                if text_box:
                    state = text_box.cget('state')  
                    if state == 'disabled':
                        text_box.config(state='normal')
                    text_box.delete(0, tk.END) 
                    if state == 'disabled':
                        text_box.config(state='disabled')
                else:
                    print(f"Text box for DID {did_key} not found.")
        except Exception as e:
            print(f"Error clearing text boxes: {e}")

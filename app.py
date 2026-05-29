#!/usr/bin/env python3
"""
UT33C+ Big Screen UI & Logger (Direct UART Version)
Enhanced with Dark Theme, Settings, and Overlay Mode.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time
import queue
import csv
from datetime import datetime

from ut33c.config import LOG_DIR, SNAPSHOT_CSV
from ut33c.ports import find_display_port, list_all_ports
from ut33c.decoder import BAUD, decode_frame, pop_next_frame

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import collections
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Colors for Dark Theme
BG_DARK = "#121212"
BG_LIGHT = "#1e1e1e"
BG_ACCENT = "#2d2d2d"
FG_PRIMARY = "#ffffff"
FG_SECONDARY = "#aaaaaa"
ACCENT_GREEN = "#00ff00"
ACCENT_BLUE = "#008CBA"
ACCENT_RED = "#cc3333"

class App(tk.Tk):
    def __init__(self, target_port=None):
        super().__init__()
        self.target_port = target_port

        self.title("UT33C+ Wireless Dashboard")
        self.geometry("900x650")
        self.configure(bg=BG_DARK)
        self.minsize(800, 500)

        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # State Variables
        self.data_queue = queue.Queue()
        self.current_reading = ("WAITING", "----", "", "")
        
        # UI State
        self.is_logging = False
        self.log_file = None
        self.csv_writer = None
        self.font_size = tk.IntVar(value=120)
        self.scale_factor = tk.DoubleVar(value=1.0)
        self.is_overlay = False
        
        # Graphing State
        self.max_points = 200
        self.graph_mode = None
        if HAS_MATPLOTLIB:
            self.x_data = collections.deque(maxlen=self.max_points)
            self.y_data = collections.deque(maxlen=self.max_points)
            self.start_time = time.time()
        
        # Apply Styles
        self._setup_styles()
        
        # Build UI
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._setup_live_tab()
        self._setup_graph_tab()
        self._setup_snapshot_tab()
        self._setup_settings_tab()

        # Status Bar (Bottom)
        self.status_frame = tk.Frame(self, bg=BG_DARK)
        self.status_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        self.lbl_status = tk.Label(self.status_frame, text="Initializing...", 
                                   font=("Helvetica", 10), 
                                   fg=FG_SECONDARY, bg=BG_DARK, anchor="w")
        self.lbl_status.pack(side="left", fill="x", expand=True)

        # Overlay Window State
        self.overlay_win = None

        # Threading and Serial state
        self.ser_active = None
        self.running = True
        self.serial_thread = threading.Thread(target=self._read_serial_loop, daemon=True)
        self.serial_thread.start()

        # Update loop
        self.after(50, self._process_queue)
        
        if HAS_MATPLOTLIB:
            self.after(1000, self._update_graph)

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Notebook / Tabs
        self.style.configure('TNotebook', background=BG_DARK, borderwidth=0)
        self.style.configure('TNotebook.Tab', padding=[20, 5], font=('Helvetica', 11),
                            background=BG_ACCENT, foreground=FG_SECONDARY)
        self.style.map('TNotebook.Tab', 
                       background=[('selected', BG_LIGHT)],
                       foreground=[('selected', FG_PRIMARY)])

        # Treeview (Snapshots)
        self.style.configure("Treeview", background=BG_LIGHT, foreground=FG_PRIMARY, 
                             fieldbackground=BG_LIGHT, borderwidth=0, font=('Helvetica', 10))
        self.style.configure("Treeview.Heading", background=BG_ACCENT, foreground=FG_PRIMARY, 
                             relief="flat", font=('Helvetica', 10, 'bold'))
        self.style.map("Treeview", background=[('selected', ACCENT_BLUE)])

        # Combobox
        self.style.configure("TCombobox", fieldbackground=BG_ACCENT, background=BG_ACCENT, 
                             foreground=FG_PRIMARY, arrowcolor=FG_PRIMARY)

    def _setup_live_tab(self):
        self.tab_live = tk.Frame(self.notebook, bg=BG_LIGHT)
        self.notebook.add(self.tab_live, text=" Live View ")

        self.tab_live.rowconfigure(0, weight=1)
        self.tab_live.rowconfigure(1, weight=3)
        self.tab_live.columnconfigure(0, weight=1)

        self.lbl_mode = tk.Label(self.tab_live, text="WAITING FOR DATA", 
                                 font=("Helvetica", 36, "bold"), 
                                 fg=FG_SECONDARY, bg=BG_LIGHT)
        self.lbl_mode.grid(row=0, column=0, sticky="s", pady=(20, 0))

        self.val_frame = tk.Frame(self.tab_live, bg=BG_LIGHT)
        self.val_frame.grid(row=1, column=0)
        
        self.lbl_value = tk.Label(self.val_frame, text="----", 
                                  font=("Helvetica", self.font_size.get(), "bold"), 
                                  fg=ACCENT_GREEN, bg=BG_LIGHT)
        self.lbl_value.pack(side="left", padx=10)
        
        self.lbl_unit = tk.Label(self.val_frame, text="", 
                                 font=("Helvetica", int(self.font_size.get()*0.5), "bold"), 
                                 fg=FG_PRIMARY, bg=BG_LIGHT)
        self.lbl_unit.pack(side="left", padx=10, pady=(int(self.font_size.get()*0.3), 0))

    def _setup_graph_tab(self):
        self.tab_graph = tk.Frame(self.notebook, bg=BG_ACCENT)
        self.notebook.add(self.tab_graph, text=" Graph & Logging ")

        # Top Control Bar
        control_frame = tk.Frame(self.tab_graph, bg=BG_ACCENT)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.btn_toggle_log = tk.Button(control_frame, text="Start Logging", 
                                        font=("Helvetica", 11, "bold"), bg="#4CAF50", fg="white",
                                        command=self._toggle_logging, width=15, relief="flat")
        self.btn_toggle_log.pack(side="left", padx=5)

        tk.Label(control_frame, text="Log Name:", font=("Helvetica", 11), 
                 bg=BG_ACCENT, fg=FG_PRIMARY).pack(side="left", padx=(15, 5))
        
        self.entry_log_name = tk.Entry(control_frame, font=("Helvetica", 11), width=15, 
                                       bg=BG_LIGHT, fg=FG_PRIMARY, insertbackground=FG_PRIMARY)
        self.entry_log_name.pack(side="left", padx=5)
        self.entry_log_name.insert(0, "ut33c_log")

        self.lbl_log_status = tk.Label(control_frame, text="Not Logging", 
                                       font=("Helvetica", 11), bg=BG_ACCENT, fg=FG_SECONDARY)
        self.lbl_log_status.pack(side="left", padx=15)

        # Graph Area
        self.graph_frame = tk.Frame(self.tab_graph, bg="black")
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if HAS_MATPLOTLIB:
            self.fig = Figure(figsize=(6, 4), dpi=100, facecolor=BG_ACCENT)
            self.ax = self.fig.add_subplot(111)
            self.ax.set_facecolor('black')
            self.ax.tick_params(colors='white')
            self.ax.spines['bottom'].set_color('white')
            self.ax.spines['left'].set_color('white')
            self.ax.spines['top'].set_color(BG_ACCENT)
            self.ax.spines['right'].set_color(BG_ACCENT)
            
            self.line, = self.ax.plot([], [], color=ACCENT_GREEN, linewidth=2)
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            lbl_no_graph = tk.Label(self.graph_frame, text="Matplotlib missing.", 
                                    font=("Helvetica", 16), fg=ACCENT_RED, bg="black")
            lbl_no_graph.pack(expand=True)

    def _setup_snapshot_tab(self):
        self.tab_snap = tk.Frame(self.notebook, bg=BG_ACCENT)
        self.notebook.add(self.tab_snap, text=" Snapshots ")

        self.snap_paned = tk.PanedWindow(self.tab_snap, orient="horizontal", bg=BG_DARK, sashwidth=4)
        self.snap_paned.pack(fill="both", expand=True)

        # --- Left Pane: Save Form ---
        self.snap_form = tk.Frame(self.snap_paned, bg=BG_ACCENT, width=350)
        self.snap_paned.add(self.snap_form)

        container = tk.Frame(self.snap_form, bg=BG_ACCENT)
        container.place(relx=0.5, rely=0.4, anchor="center")

        self.lbl_snap_reading = tk.Label(container, text="----", 
                                         font=("Helvetica", 36, "bold"), 
                                         fg="#00aaaa", bg=BG_ACCENT)
        self.lbl_snap_reading.pack(pady=10)

        tk.Label(container, text="Snapshot Name:", 
                            font=("Helvetica", 12), bg=BG_ACCENT, fg=FG_PRIMARY).pack(pady=(10, 5))

        self.entry_snap_name = tk.Entry(container, font=("Helvetica", 12), width=20, 
                                        bg=BG_LIGHT, fg=FG_PRIMARY, insertbackground=FG_PRIMARY)
        self.entry_snap_name.pack(pady=5)
        self.entry_snap_name.bind('<Return>', lambda e: self._save_snapshot())

        self.btn_save_snap = tk.Button(container, text="Save Snapshot", 
                                       font=("Helvetica", 12, "bold"), bg=ACCENT_BLUE, fg="white",
                                       command=self._save_snapshot, width=15, relief="flat")
        self.btn_save_snap.pack(pady=15)

        self.lbl_snap_feedback = tk.Label(container, text="", 
                                          font=("Helvetica", 10), bg=BG_ACCENT, fg=ACCENT_GREEN)
        self.lbl_snap_feedback.pack(pady=5)

        # --- Right Pane: List ---
        self.snap_list_frame = tk.Frame(self.snap_paned, bg=BG_DARK)
        self.snap_paned.add(self.snap_list_frame)

        lbl_list_title = tk.Label(self.snap_list_frame, text="Snapshot History", 
                                  font=("Helvetica", 12, "bold"), fg=FG_PRIMARY, bg=BG_ACCENT)
        lbl_list_title.pack(fill="x", pady=(0, 5))

        tree_frame = tk.Frame(self.snap_list_frame, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree_snaps = ttk.Treeview(tree_frame, columns=("Time", "Name", "Mode", "Value", "Unit"), 
                                       show="headings", yscrollcommand=scrollbar.set)
        
        self.tree_snaps.heading("Time", text="Time")
        self.tree_snaps.heading("Name", text="Name")
        self.tree_snaps.heading("Mode", text="Mode")
        self.tree_snaps.heading("Value", text="Value")
        self.tree_snaps.heading("Unit", text="Unit")

        for col, width in [("Time", 100), ("Name", 120), ("Mode", 80), ("Value", 80), ("Unit", 60)]:
            self.tree_snaps.column(col, width=width, anchor="center")

        self.tree_snaps.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree_snaps.yview)

        btn_frame = tk.Frame(self.snap_list_frame, bg=BG_ACCENT)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Refresh List", bg="#444444", fg="white", 
                  command=self._load_snapshots, width=12, relief="flat").pack(side="left", fill="x", expand=True)
        tk.Button(btn_frame, text="Delete Selected", bg=ACCENT_RED, fg="white", 
                  command=self._delete_selected_snapshot, width=12, relief="flat").pack(side="left", fill="x", expand=True)

        self.after(100, self._load_snapshots)

    def _setup_settings_tab(self):
        self.tab_settings = tk.Frame(self.notebook, bg=BG_LIGHT)
        self.notebook.add(self.tab_settings, text=" Settings ")

        # --- Section: Connectivity ---
        sec_conn = tk.LabelFrame(self.tab_settings, text="Connectivity", bg=BG_LIGHT, fg=ACCENT_BLUE, 
                                 font=("Helvetica", 11, "bold"), padx=20, pady=10)
        sec_conn.pack(fill="x", padx=20, pady=10)

        tk.Label(sec_conn, text="COM Port:", bg=BG_LIGHT, fg=FG_PRIMARY).pack(side="left")
        
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(sec_conn, textvariable=self.port_var, 
                                          values=list_all_ports(), state="readonly", width=40)
        self.port_dropdown.pack(side="left", padx=10)
        self.port_dropdown.bind("<<ComboboxSelected>>", lambda e: self._switch_port())
        
        tk.Button(sec_conn, text="Refresh", bg=BG_ACCENT, fg="white", 
                  command=self._refresh_ports_list, relief="flat").pack(side="left")

        tk.Button(sec_conn, text="Connect", bg=ACCENT_BLUE, fg="white", 
                  command=self._apply_port_change, relief="flat", width=10).pack(side="left", padx=10)

        tk.Button(sec_conn, text="Pair Bluetooth Device", bg="#444444", fg="white", 
                  command=self._open_bt_settings, relief="flat").pack(side="left", padx=10)

        # --- Section: Appearance ---
        sec_app = tk.LabelFrame(self.tab_settings, text="Appearance", bg=BG_LIGHT, fg=ACCENT_BLUE, 
                                 font=("Helvetica", 11, "bold"), padx=20, pady=10)
        sec_app.pack(fill="x", padx=20, pady=10)

        # Font Size
        tk.Label(sec_app, text="Main Font Size:", bg=BG_LIGHT, fg=FG_PRIMARY).grid(row=0, column=0, sticky="w")
        scale_font = tk.Scale(sec_app, from_=40, to=300, orient="horizontal", variable=self.font_size, 
                              bg=BG_LIGHT, fg=FG_PRIMARY, highlightthickness=0, command=self._update_ui_scaling)
        scale_font.grid(row=0, column=1, padx=10, sticky="ew")

        # Scale Factor
        tk.Label(sec_app, text="Global Scaling:", bg=BG_LIGHT, fg=FG_PRIMARY).grid(row=1, column=0, sticky="w")
        scale_glob = tk.Scale(sec_app, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", variable=self.scale_factor,
                               bg=BG_LIGHT, fg=FG_PRIMARY, highlightthickness=0)
        scale_glob.grid(row=1, column=1, padx=10, sticky="ew")

        # --- Section: Overlay Mode ---
        sec_ov = tk.LabelFrame(self.tab_settings, text="Overlay Mode", bg=BG_LIGHT, fg=ACCENT_BLUE, 
                                 font=("Helvetica", 11, "bold"), padx=20, pady=10)
        sec_ov.pack(fill="x", padx=20, pady=10)

        tk.Label(sec_ov, text="Show live reading as a transparent overlay on top of other windows.", 
                 bg=BG_LIGHT, fg=FG_SECONDARY, font=("Helvetica", 9)).pack(anchor="w")

        self.btn_overlay = tk.Button(sec_ov, text="Enable Overlay Mode", font=("Helvetica", 11, "bold"),
                                     bg=ACCENT_BLUE, fg="white", command=self._toggle_overlay, relief="flat", pady=5)
        self.btn_overlay.pack(pady=10, fill="x")

    def _open_bt_settings(self):
        import os
        try:
            os.system("start ms-settings:bluetooth")
        except:
            messagebox.showinfo("Bluetooth", "Please open Bluetooth Settings in Windows to pair your device.")

    def _apply_port_change(self):
        # Extract COM port from dropdown string
        full_val = self.port_var.get()
        new_port = full_val.split(" - ")[0] if " - " in full_val else full_val
        
        if new_port:
            self.target_port = new_port
            self.lbl_status.config(text=f"Forcing connection to {new_port}...")
            # If a connection is active, closing it will break the blocking read loop
            if self.ser_active:
                try:
                    self.ser_active.close()
                except: pass

    def _refresh_ports_list(self):
        ports = list_all_ports()
        self.port_dropdown.config(values=ports)
        self.lbl_status.config(text=f"Refreshed ports. Found {len(ports)} devices.")

    def _switch_port(self):
        # Extract COM port from "COMx - Description"
        full_val = self.port_var.get()
        new_port = full_val.split(" - ")[0] if " - " in full_val else full_val
        if new_port:
            self.target_port = new_port
            self.lbl_status.config(text=f"Switching to port {new_port}...")

    def _ov_scroll_scale(self, event):
        # Windows event.delta is typically 120 or -120
        delta = 10 if event.delta > 0 else -10
        self._adjust_font(delta)

    def _adjust_font(self, delta):
        new_size = self.font_size.get() + delta
        if 20 <= new_size <= 500:
            self.font_size.set(new_size)
            self._update_ui_scaling()

    def _update_ui_scaling(self, *args):
        # Update main labels
        fsize = self.font_size.get()
        self.lbl_value.config(font=("Helvetica", fsize, "bold"))
        self.lbl_unit.config(font=("Helvetica", int(fsize*0.5), "bold"))
        self.lbl_unit.pack_configure(pady=(int(fsize*0.3), 0))
        
        # Update overlay if active
        if self.overlay_win and self.overlay_win.winfo_exists():
            self.lbl_ov_value.config(font=("Helvetica", fsize, "bold"))
            self.lbl_ov_unit.config(font=("Helvetica", int(fsize*0.4), "bold"))
            self.lbl_ov_unit.pack_configure(pady=(int(fsize*0.3), 0))

    def _toggle_overlay(self):
        if self.is_overlay:
            self.is_overlay = False
            self.btn_overlay.config(text="Enable Overlay Mode", bg=ACCENT_BLUE)
            if self.overlay_win:
                self.overlay_win.destroy()
                self.overlay_win = None
            self.deiconify() # Show main window
        else:
            self.is_overlay = True
            self.btn_overlay.config(text="Disable Overlay Mode (Press ESC to exit)", bg=ACCENT_RED)
            self.withdraw() # Hide main window
            self._create_overlay_window()

    def _create_overlay_window(self):
        self.overlay_win = tk.Toplevel(self)
        self.overlay_win.title("UT33C+ Overlay")
        self.overlay_win.attributes("-topmost", True)
        self.overlay_win.attributes("-alpha", 0.9) # Slightly less transparent for better visibility
        self.overlay_win.overrideredirect(True) # No borders
        self.overlay_win.configure(bg="black")
        
        # Make transparent-ish but keep text visible
        self.overlay_win.attributes("-transparentcolor", "black")

        # Context Menu for exit
        self.ov_menu = tk.Menu(self.overlay_win, tearoff=0, bg=BG_ACCENT, fg=FG_PRIMARY)
        self.ov_menu.add_command(label="Exit Overlay (ESC)", command=self._toggle_overlay)
        self.ov_menu.add_separator()
        self.ov_menu.add_command(label="Close Application", command=self.destroy)

        # Bindings
        self.overlay_win.bind("<Button-1>", self._start_drag)
        self.overlay_win.bind("<B1-Motion>", self._do_drag)
        self.overlay_win.bind("<Button-3>", self._show_ov_menu) # Right click
        self.overlay_win.bind("<Escape>", lambda e: self._toggle_overlay())
        
        # Scaling shortcuts in Overlay
        self.overlay_win.bind("<Control-MouseWheel>", self._ov_scroll_scale) # Windows Scroll
        self.overlay_win.bind("<plus>", lambda e: self._adjust_font(10))
        self.overlay_win.bind("<equal>", lambda e: self._adjust_font(10))
        self.overlay_win.bind("<minus>", lambda e: self._adjust_font(-10))

        self.ov_frame = tk.Frame(self.overlay_win, bg="black")
        self.ov_frame.pack(padx=10, pady=10)

        fsize = self.font_size.get()
        self.lbl_ov_value = tk.Label(self.ov_frame, text="----", font=("Helvetica", fsize, "bold"), 
                                     fg=ACCENT_GREEN, bg="black")
        self.lbl_ov_value.pack(side="left")
        
        self.lbl_ov_unit = tk.Label(self.ov_frame, text="", font=("Helvetica", int(fsize*0.4), "bold"), 
                                    fg=FG_PRIMARY, bg="black")
        self.lbl_ov_unit.pack(side="left", padx=5, pady=(int(fsize*0.3), 0))

    def _show_ov_menu(self, event):
        self.ov_menu.post(event.x_root, event.y_root)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        x = self.overlay_win.winfo_x() + (event.x - self._drag_x)
        y = self.overlay_win.winfo_y() + (event.y - self._drag_y)
        self.overlay_win.geometry(f"+{x}+{y}")

    def update_reading(self, mode, val, unit, raw_hex):
        self.current_reading = (mode, val, unit, raw_hex)
        
        # Update Main UI
        try:
            self.lbl_mode.config(text=mode.upper())
            self.lbl_value.config(text=val)
            self.lbl_unit.config(text=unit)
            self.lbl_value.config(fg="#ffaa00" if val in ("OL", "???") else ACCENT_GREEN)
            self.lbl_snap_reading.config(text=f"{val} {unit}")
        except: pass

        # Update Overlay
        if self.overlay_win and self.overlay_win.winfo_exists():
            try:
                self.lbl_ov_value.config(text=val)
                self.lbl_ov_unit.config(text=unit)
                self.lbl_ov_value.config(fg="#ffaa00" if val in ("OL", "???") else ACCENT_GREEN)
            except: pass

        if self.is_logging and self.csv_writer:
            self.csv_writer.writerow([datetime.now().isoformat(), mode, val, unit, raw_hex])
            self.log_file.flush()

        if HAS_MATPLOTLIB:
            try:
                if mode != self.graph_mode:
                    self.x_data.clear()
                    self.y_data.clear()
                    self.graph_mode = mode
                    self.start_time = time.time()
                    self.ax.set_title(f"Mode: {mode}", color='white')
                
                if val not in ("OL", "???"):
                    self.x_data.append(time.time() - self.start_time)
                    self.y_data.append(float(val))
            except: pass

    def _update_graph(self):
        if self.running and HAS_MATPLOTLIB and len(self.x_data) > 1:
            self.line.set_data(list(self.x_data), list(self.y_data))
            self.ax.relim(); self.ax.autoscale_view(); self.canvas.draw()
        self.after(500, self._update_graph)

    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.data_queue.get_nowait()
                if msg_type == "reading": self.update_reading(*data)
                elif msg_type == "status": self.lbl_status.config(text=data)
        except queue.Empty: pass
        if self.running: self.after(50, self._process_queue)

    def _read_serial_loop(self):
        port = self.target_port
        while self.running:
            if not port:
                port = find_display_port()
                if not port:
                    self.data_queue.put(("status", "Searching for device..."))
                    time.sleep(2); continue

            self.data_queue.put(("status", f"Connecting to {port}..."))
            try:
                # Increased timeout to 0.5 for BT stability
                self.ser_active = serial.Serial(port, BAUD, timeout=0.5)
                with self.ser_active as ser:
                    self.data_queue.put(("status", f"Connected to {port}"))
                    buffer = bytearray()
                    invalid_bytes = 0
                    last_data_time = time.time()
                    
                    while self.running and self.target_port in (None, port):
                        # Blocking read with timeout
                        new_data = ser.read(32) 
                        if new_data:
                            last_data_time = time.time() # Reset inactivity timer
                            buffer.extend(new_data)
                            frames_found = 0
                            while True:
                                frame = pop_next_frame(buffer)
                                if frame is None: break
                                frames_found += 1
                                r = decode_frame(frame)
                                self.data_queue.put(("reading", (r.mode, r.value, r.unit, r.raw_hex)))
                            
                            # Relaxed data integrity check
                            if frames_found == 0 and len(buffer) > 100:
                                invalid_bytes += len(new_data)
                                if invalid_bytes > 500:
                                    self.data_queue.put(("status", "WARNING: Data Sync Error. Check meter."))
                                    del buffer[:-10]
                            else:
                                invalid_bytes = 0
                        else:
                            # If we get no data for 5 seconds, assume silent disconnect
                            if time.time() - last_data_time > 5.0:
                                self.data_queue.put(("status", "Inactivity Timeout: Meter silent for 5s."))
                                break # Exit inner loop to trigger reconnect/search
                        
                        time.sleep(0.01)
                self.ser_active = None # Clear after loop exit
                port = self.target_port # Pick up dynamic change
            except Exception as e:
                self.ser_active = None
                err_msg = str(e).split('\n')[0][:40]
                self.data_queue.put(("status", f"Link Lost: {err_msg}... Retrying."))
                if not self.target_port: port = None
                time.sleep(2)

    def _toggle_logging(self):
        if self.is_logging:
            self.is_logging = False
            if self.log_file: self.log_file.close(); self.log_file = None
            self.btn_toggle_log.config(text="Start Logging", bg="#4CAF50")
            self.lbl_log_status.config(text="Stopped.", fg=FG_SECONDARY)
        else:
            base = self.entry_log_name.get().strip() or "ut33c_log"
            filename = f"{base}_{int(time.time())}.csv"
            try:
                self.log_file = (LOG_DIR / filename).open("w", newline="")
                self.csv_writer = csv.writer(self.log_file)
                self.csv_writer.writerow(["Timestamp", "Mode", "Value", "Unit", "Raw_Hex"])
                self.is_logging = True
                self.btn_toggle_log.config(text="Stop Logging", bg=ACCENT_RED)
                self.lbl_log_status.config(text=f"Logging: {filename}", fg=ACCENT_GREEN)
            except Exception as e: messagebox.showerror("Error", str(e))

    def _save_snapshot(self):
        m, v, u, h = self.current_reading
        if v == "----": return
        name = self.entry_snap_name.get().strip()
        if not name: return
        try:
            path = LOG_DIR / SNAPSHOT_CSV
            exists = path.exists()
            with path.open("a", newline="") as f:
                w = csv.writer(f)
                if not exists: w.writerow(["Timestamp", "Name", "Mode", "Value", "Unit", "Raw_Hex"])
                w.writerow([datetime.now().isoformat(), name, m, v, u, h])
            self._load_snapshots()
            self.lbl_snap_feedback.config(text="Saved!", fg=ACCENT_GREEN)
            self.entry_snap_name.delete(0, tk.END)
            self.after(2000, lambda: self.lbl_snap_feedback.config(text=""))
        except Exception as e: messagebox.showerror("Error", str(e))

    def _delete_selected_snapshot(self):
        sel = self.tree_snaps.selection()
        if not sel: return
        item = self.tree_snaps.item(sel[0])
        if not messagebox.askyesno("Delete", f"Delete '{item['values'][1]}'?"): return
        try:
            rows = []
            path = LOG_DIR / SNAPSHOT_CSV
            with path.open("r", newline="") as f:
                reader = csv.reader(f); head = next(reader, None); rows = list(reader)
            new_rows = [r for r in rows if not (item['values'][1] == r[1] and item['values'][0] in r[0])]
            with path.open("w", newline="") as f:
                writer = csv.writer(f); writer.writerow(head); writer.writerows(new_rows)
            self._load_snapshots()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _load_snapshots(self):
        for i in self.tree_snaps.get_children(): self.tree_snaps.delete(i)
        path = LOG_DIR / SNAPSHOT_CSV
        if not path.exists(): return
        try:
            with path.open("r", newline="") as f:
                reader = csv.reader(f); next(reader, None)
                for r in reversed(list(reader)):
                    try: ts = datetime.fromisoformat(r[0]).strftime("%H:%M:%S")
                    except: ts = r[0]
                    self.tree_snaps.insert("", "end", values=(ts, r[1], r[2], r[3], r[4]))
        except: pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=None)
    args = parser.parse_args()
    app = App(target_port=args.port)
    try: app.mainloop()
    except KeyboardInterrupt: pass
    finally:
        app.running = False
        if app.log_file: app.log_file.close()

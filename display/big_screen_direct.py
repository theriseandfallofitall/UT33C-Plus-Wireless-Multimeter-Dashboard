#!/usr/bin/env python3
"""
UT33C+ Big Screen UI & Logger (Direct UART Version)
Reads raw binary telemetry data from the UT33C+ directly (for example, via
FTDI, CH340, or Pico passthrough). It does not send commands, control power,
or interact with the Pico command rig.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time
import queue
import csv
from datetime import datetime

from display.config import LOG_DIR, SNAPSHOT_CSV
from display.ports import find_display_port
from display.protocol import BAUD, decode_frame, pop_next_frame

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import collections
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("UT33C+ Big Screen & Logger (Direct UART)")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")
        self.minsize(800, 500)

        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # State Variables
        self.data_queue = queue.Queue()
        self.current_reading = ("WAITING", "----", "", "")
        
        # Logging State
        self.is_logging = False
        self.log_file = None
        self.csv_writer = None

        # Graphing State
        self.max_points = 200
        self.graph_mode = None
        if HAS_MATPLOTLIB:
            self.x_data = collections.deque(maxlen=self.max_points)
            self.y_data = collections.deque(maxlen=self.max_points)
            self.start_time = time.time()
        
        # Build UI
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TNotebook.Tab', padding=[20, 5], font=('Helvetica', 12))
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._setup_live_tab()
        self._setup_graph_tab()
        self._setup_snapshot_tab()

        # Status Bar (Bottom)
        self.lbl_status = tk.Label(self, text="Initializing...", 
                                   font=("Helvetica", 10), 
                                   fg="#888888", bg="#1e1e1e", anchor="w")
        self.lbl_status.pack(side="bottom", fill="x", padx=10, pady=5)

        # Threading and Serial state
        self.running = True
        self.serial_thread = threading.Thread(target=self._read_serial_loop, daemon=True)
        self.serial_thread.start()

        # Update loop
        self.after(50, self._process_queue)
        
        if HAS_MATPLOTLIB:
            self.after(1000, self._update_graph)

    def _setup_live_tab(self):
        self.tab_live = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.tab_live, text="Live View")

        self.tab_live.rowconfigure(0, weight=1)
        self.tab_live.rowconfigure(1, weight=3)
        self.tab_live.columnconfigure(0, weight=1)

        self.lbl_mode = tk.Label(self.tab_live, text="WAITING FOR DATA", 
                                 font=("Helvetica", 36, "bold"), 
                                 fg="#aaaaaa", bg="#1e1e1e")
        self.lbl_mode.grid(row=0, column=0, sticky="s", pady=(20, 0))

        self.val_frame = tk.Frame(self.tab_live, bg="#1e1e1e")
        self.val_frame.grid(row=1, column=0)
        
        self.lbl_value = tk.Label(self.val_frame, text="----", 
                                  font=("Helvetica", 120, "bold"), 
                                  fg="#00ff00", bg="#1e1e1e")
        self.lbl_value.pack(side="left", padx=10)
        
        self.lbl_unit = tk.Label(self.val_frame, text="", 
                                 font=("Helvetica", 60, "bold"), 
                                 fg="#ffffff", bg="#1e1e1e")
        self.lbl_unit.pack(side="left", padx=10, pady=(40, 0))

    def _setup_graph_tab(self):
        self.tab_graph = tk.Frame(self.notebook, bg="#2d2d2d")
        self.notebook.add(self.tab_graph, text="Graph & Logging")

        # Top Control Bar
        control_frame = tk.Frame(self.tab_graph, bg="#2d2d2d")
        control_frame.pack(fill="x", padx=10, pady=10)

        self.btn_toggle_log = tk.Button(control_frame, text="Start Logging", 
                                        font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                                        command=self._toggle_logging, width=15)
        self.btn_toggle_log.pack(side="left", padx=5)

        self.lbl_log_status = tk.Label(control_frame, text="Not Logging", 
                                       font=("Helvetica", 12), bg="#2d2d2d", fg="#aaaaaa")
        self.lbl_log_status.pack(side="left", padx=15)

        # Graph Area
        self.graph_frame = tk.Frame(self.tab_graph, bg="black")
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if HAS_MATPLOTLIB:
            self.fig = Figure(figsize=(6, 4), dpi=100, facecolor='#2d2d2d')
            self.ax = self.fig.add_subplot(111)
            self.ax.set_facecolor('black')
            self.ax.tick_params(colors='white')
            self.ax.spines['bottom'].set_color('white')
            self.ax.spines['left'].set_color('white')
            self.ax.spines['top'].set_color('#2d2d2d')
            self.ax.spines['right'].set_color('#2d2d2d')
            
            self.line, = self.ax.plot([], [], color='#00ff00', linewidth=2)
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            lbl_no_graph = tk.Label(self.graph_frame, text="Matplotlib is required for graphing.\nInstall with: pip install matplotlib", 
                                    font=("Helvetica", 16), fg="#ff5555", bg="black")
            lbl_no_graph.pack(expand=True)

    def _setup_snapshot_tab(self):
        self.tab_snap = tk.Frame(self.notebook, bg="#2d2d2d")
        self.notebook.add(self.tab_snap, text="Snapshots")

        # Split into Left (Form) and Right (List)
        self.snap_paned = tk.PanedWindow(self.tab_snap, orient="horizontal", bg="#2d2d2d", sashwidth=4)
        self.snap_paned.pack(fill="both", expand=True)

        # --- Left Pane: Save Form ---
        self.snap_form = tk.Frame(self.snap_paned, bg="#2d2d2d", width=350)
        self.snap_paned.add(self.snap_form)

        container = tk.Frame(self.snap_form, bg="#2d2d2d")
        container.place(relx=0.5, rely=0.4, anchor="center")

        # Current Reading display
        self.lbl_snap_reading = tk.Label(container, text="----", 
                                         font=("Helvetica", 36, "bold"), 
                                         fg="#00aaaa", bg="#2d2d2d")
        self.lbl_snap_reading.pack(pady=10)

        # Name Entry
        lbl_name = tk.Label(container, text="Snapshot Name:", 
                            font=("Helvetica", 14), bg="#2d2d2d", fg="white")
        lbl_name.pack(pady=(10, 5))

        self.entry_snap_name = tk.Entry(container, font=("Helvetica", 14), width=20)
        self.entry_snap_name.pack(pady=5)
        # Allow hitting Enter to save
        self.entry_snap_name.bind('<Return>', lambda e: self._save_snapshot())

        self.btn_save_snap = tk.Button(container, text="Save Snapshot", 
                                       font=("Helvetica", 14, "bold"), bg="#008CBA", fg="white",
                                       command=self._save_snapshot, width=15)
        self.btn_save_snap.pack(pady=15)

        self.lbl_snap_feedback = tk.Label(container, text="", 
                                          font=("Helvetica", 10), bg="#2d2d2d", fg="#00ff00")
        self.lbl_snap_feedback.pack(pady=5)

        # --- Right Pane: Snapshot List ---
        self.snap_list_frame = tk.Frame(self.snap_paned, bg="#1e1e1e")
        self.snap_paned.add(self.snap_list_frame)

        # Header
        lbl_list_title = tk.Label(self.snap_list_frame, text="Snapshot History", 
                                  font=("Helvetica", 14, "bold"), fg="#ffffff", bg="#333333")
        lbl_list_title.pack(fill="x", pady=(0, 5))

        # Scrollbar and Treeview
        tree_frame = tk.Frame(self.snap_list_frame, bg="#1e1e1e")
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

        self.tree_snaps.column("Time", width=120)
        self.tree_snaps.column("Name", width=120)
        self.tree_snaps.column("Mode", width=100)
        self.tree_snaps.column("Value", width=80, anchor="center")
        self.tree_snaps.column("Unit", width=60, anchor="center")

        self.tree_snaps.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree_snaps.yview)

        # Refresh Button
        self.btn_refresh_snaps = tk.Button(self.snap_list_frame, text="Refresh List", 
                                           bg="#555555", fg="white", command=self._load_snapshots)
        self.btn_refresh_snaps.pack(fill="x")

        # Initial Load
        self.after(100, self._load_snapshots)

    def _load_snapshots(self):
        # Clear current list
        for item in self.tree_snaps.get_children():
            self.tree_snaps.delete(item)

        filepath = LOG_DIR / SNAPSHOT_CSV
        if not filepath.exists():
            return

        try:
            with filepath.open("r", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    return

                # Read rows and insert into tree (reverse order to show newest first)
                rows = list(reader)
                for row in reversed(rows):
                    if len(row) >= 5:
                        # Convert ISO timestamp to more readable format
                        try:
                            ts = datetime.fromisoformat(row[0]).strftime("%H:%M:%S")
                        except ValueError:
                            ts = row[0]
                        
                        self.tree_snaps.insert("", "end", values=(ts, row[1], row[2], row[3], row[4]))
        except Exception as e:
            print(f"Error loading snapshots: {e}")


    def _toggle_logging(self):
        if self.is_logging:
            # Stop Logging
            self.is_logging = False
            if self.log_file:
                self.log_file.close()
                self.log_file = None
            self.btn_toggle_log.config(text="Start Logging", bg="#4CAF50")
            self.lbl_log_status.config(text="Logging Stopped.", fg="#aaaaaa")
        else:
            # Start Logging
            filename = f"ut33c_log_{int(time.time())}.csv"
            filepath = LOG_DIR / filename
            try:
                self.log_file = filepath.open("w", newline="")
                self.csv_writer = csv.writer(self.log_file)
                self.csv_writer.writerow(["Timestamp", "Mode", "Value", "Unit", "Raw_Hex"])
                self.is_logging = True
                
                self.btn_toggle_log.config(text="Stop Logging", bg="#f44336")
                self.lbl_log_status.config(text=f"Logging to: {filename}", fg="#00ff00")
            except Exception as e:
                messagebox.showerror("Logging Error", f"Could not open log file: {e}")

    def _save_snapshot(self):
        mode, val, unit, raw_hex = self.current_reading
        if val == "----" or mode == "WAITING":
            self.lbl_snap_feedback.config(text="Error: No valid reading to save.", fg="#ff5555")
            return

        name = self.entry_snap_name.get().strip()
        if not name:
            self.lbl_snap_feedback.config(text="Error: Please enter a name.", fg="#ff5555")
            return

        filepath = LOG_DIR / SNAPSHOT_CSV
        file_exists = filepath.exists()
        
        try:
            with filepath.open("a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "Name", "Mode", "Value", "Unit", "Raw_Hex"])
                
                timestamp = datetime.now().isoformat()
                writer.writerow([timestamp, name, mode, val, unit, raw_hex])
            
            self.lbl_snap_feedback.config(text=f"Saved: {name} = {val} {unit}", fg="#00ff00")
            self.entry_snap_name.delete(0, tk.END)
            # Clear feedback after 3 seconds
            self.after(3000, lambda: self.lbl_snap_feedback.config(text=""))
            
        except Exception as e:
            messagebox.showerror("Snapshot Error", f"Could not save snapshot: {e}")

    def update_reading(self, mode, val, unit, raw_hex):
        self.current_reading = (mode, val, unit, raw_hex)
        
        # 1. Update Live View
        self.lbl_mode.config(text=mode.upper())
        self.lbl_value.config(text=val)
        self.lbl_unit.config(text=unit)
        
        if val == "OL" or val == "???":
            self.lbl_value.config(fg="#ffaa00")
        else:
            self.lbl_value.config(fg="#00ff00")

        # 2. Update Snapshot view
        self.lbl_snap_reading.config(text=f"{val} {unit}")

        # 3. Log to CSV if active
        if self.is_logging and self.csv_writer:
            timestamp = datetime.now().isoformat()
            self.csv_writer.writerow([timestamp, mode, val, unit, raw_hex])
            self.log_file.flush()

        # 4. Update Graph Data
        if HAS_MATPLOTLIB:
            try:
                # Clear graph if mode changes
                if mode != self.graph_mode:
                    self.x_data.clear()
                    self.y_data.clear()
                    self.graph_mode = mode
                    self.start_time = time.time()
                    self.ax.set_title(f"Mode: {mode}", color='white')
                    self.ax.set_ylabel(unit, color='white')

                if val != "OL" and val != "???":
                    float_val = float(val)
                    current_time = time.time() - self.start_time
                    self.x_data.append(current_time)
                    self.y_data.append(float_val)
            except ValueError:
                pass

    def _update_graph(self):
        if not self.running:
            return
            
        if HAS_MATPLOTLIB and len(self.x_data) > 1:
            self.line.set_data(list(self.x_data), list(self.y_data))
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            
        self.after(500, self._update_graph)

    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.data_queue.get_nowait()
                if msg_type == "reading":
                    self.update_reading(*data)
                elif msg_type == "status":
                    self.lbl_status.config(text=data)
        except queue.Empty:
            pass
        finally:
            if self.running:
                self.after(50, self._process_queue)

    def _read_serial_loop(self):
        port = None
        while self.running:
            if not port:
                port = find_display_port()
                if not port:
                    self.data_queue.put(("status", "Searching for device... (No COM ports found)"))
                    time.sleep(2)
                    continue

            self.data_queue.put(("status", f"Connecting to {port} at {BAUD} baud (Direct UART)..."))
            
            try:
                # Passively listen at 2400 baud. No commands sent.
                with serial.Serial(port, BAUD, timeout=0.1) as ser:
                    self.data_queue.put(("status", f"Connected to {port} (Passive Listen)"))
                    buffer = bytearray()
                    
                    while self.running:
                        if ser.in_waiting:
                            buffer.extend(ser.read(ser.in_waiting))
                            
                            while True:
                                frame = pop_next_frame(buffer)
                                if frame is None:
                                    break

                                reading = decode_frame(frame)
                                self.data_queue.put((
                                    "reading",
                                    (reading.mode, reading.value, reading.unit, reading.raw_hex),
                                ))
                        time.sleep(0.01)
            except serial.SerialException as e:
                self.data_queue.put(("status", f"Connection lost: {e}"))
                port = None
                time.sleep(2)
            except Exception as e:
                self.data_queue.put(("status", f"Error: {e}"))
                port = None
                time.sleep(2)

if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        app.running = False
        if app.log_file:
            app.log_file.close()

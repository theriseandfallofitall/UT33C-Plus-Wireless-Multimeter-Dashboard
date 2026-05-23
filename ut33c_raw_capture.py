#!/usr/bin/env python3
"""UT33C+ Structured Raw Capture Tool
Allows for manual start/stop of captures, labeled by test names.
Produces logs formatted for easy sharing and analysis.
"""
import argparse
import sys
import time
import threading
import os

try:
    import serial
except ImportError:
    print("Error: pyserial not found. Install with: pip install pyserial")
    sys.exit(1)

class CaptureSession:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.tests = []
        self.current_test = None
        self.capturing = False
        self.buffer = []
        self.stop_event = threading.Event()

    def get_serial_port():
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if not ports: return None
        print("\nAvailable Ports:")
        for i, p in enumerate(ports):
            print(f"[{i}] {p.device} ({p.description})")
        while True:
            try:
                choice = input("\nSelect port index: ").strip()
                idx = int(choice)
                if 0 <= idx < len(ports): return ports[idx].device
            except: pass
            print("Invalid selection.")

    def _capture_thread(self, ser):
        while not self.stop_event.is_set():
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                self.buffer.append(data.hex(' ').upper())
            time.sleep(0.01)

    def run_test(self):
        name = input("\nEnter Test Name (e.g., '10k Resistor 20k Range'): ").strip()
        if not name: name = f"Unnamed Test {len(self.tests) + 1}"
        
        print(f"\nREADY TO CAPTURE: {name}")
        input("Press [ENTER] to START capture...")
        
        self.buffer = []
        self.stop_event.clear()
        
        try:
            with serial.Serial(self.port, self.baud, timeout=0.1) as ser:
                thread = threading.Thread(target=self._capture_thread, args=(ser,))
                thread.start()
                
                print(">>> CAPTURING... Press [ENTER] to STOP.")
                input()
                
                self.stop_event.set()
                thread.join()
        except Exception as e:
            print(f"Serial Error: {e}")
            return

        raw_hex = " ".join(self.buffer)
        if not raw_hex:
            print("No data captured.")
            return

        print(f"Captured {len(self.buffer)} chunks of data.")
        save = input("Keep this capture? [Y/n]: ").strip().lower()
        if save != 'n':
            self.tests.append({"name": name, "hex": raw_hex})
            print("Added to session.")
        else:
            print("Discarded.")

    def save_session(self):
        if not self.tests:
            print("No tests to save.")
            return

        session_name = input("\nEnter a name for this session (for the log file): ").strip()
        if not session_name: session_name = "Capture_Session"
        
        filename = f"{session_name.replace(' ', '_')}_{int(time.time())}.log"
        
        with open(filename, "w") as f:
            f.write(f"# SESSION: {session_name}\n")
            f.write(f"# PORT: {self.port} | BAUD: {self.baud}\n")
            f.write(f"# DATE: {time.ctime()}\n\n")
            
            for test in self.tests:
                f.write(f"## TEST: {test['name']}\n")
                f.write(f"RAW_HEX: {test['hex']}\n\n")
        
        print(f"\n" + "="*40)
        print(f"SESSION SAVED TO: {filename}")
        print("="*40)
        print("\n--- CONTENT PREVIEW (Ready to pipe/copy) ---")
        with open(filename, 'r') as f:
            print(f.read())
        print("="*40)

def main():
    parser = argparse.ArgumentParser(description="Simplified Raw Capture")
    parser.add_argument("--port", help="Serial port")
    parser.add_argument("--baud", type=int, default=2400)
    args = parser.parse_args()

    port = args.port or CaptureSession.get_serial_port()
    if not port: return

    print("\n--- UT33C+ Raw Capture ---")
    test_name = input("Enter Test Name (e.g., '10k_Resistor'): ").strip()
    if not test_name: test_name = f"Capture_{int(time.time())}"

    # Setup session but we only do one test
    session = CaptureSession(port, args.baud)
    
    print(f"\nREADY TO CAPTURE: {test_name}")
    input("Press [ENTER] to START capture...")
    
    session.buffer = []
    session.stop_event.clear()
    
    try:
        with serial.Serial(session.port, session.baud, timeout=0.1) as ser:
            thread = threading.Thread(target=session._capture_thread, args=(ser,))
            thread.start()
            
            print(">>> CAPTURING... Press [ENTER] to STOP.")
            input()
            
            session.stop_event.set()
            thread.join()
    except Exception as e:
        print(f"Serial Error: {e}")
        return

    raw_hex = " ".join(session.buffer)
    if not raw_hex:
        print("No data captured.")
        return

    # Ensure logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Auto-save using the provided name inside logs directory
    base_filename = f"{test_name.replace(' ', '_')}"
    filename = os.path.join(log_dir, f"{base_filename}.log")
    
    # Ensure filename is unique if it exists
    if os.path.exists(filename):
        filename = os.path.join(log_dir, f"{base_filename}_{int(time.time())}.log")

    with open(filename, "w") as f:
        f.write(f"# TEST: {test_name}\n")
        f.write(f"# PORT: {session.port} | BAUD: {session.baud}\n")
        f.write(f"# DATE: {time.ctime()}\n\n")
        f.write(f"RAW_HEX: {raw_hex}\n")

    print(f"\n" + "="*40)
    print(f"SAVED TO: {filename}")
    print("="*40)
    print("\n--- CONTENT PREVIEW ---")
    print(f"## TEST: {test_name}")
    print(f"RAW_HEX: {raw_hex}")
    print("="*40)

if __name__ == "__main__":
    main()

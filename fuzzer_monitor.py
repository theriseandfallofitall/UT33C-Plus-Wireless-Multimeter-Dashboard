#!/usr/bin/env python3
"""
UT33C+ Fuzzer Monitor & Stream Logger
Captures output from the YD-RP2040 and saves it for later AI analysis.
"""

import serial
import serial.tools.list_ports
import time
import os
from datetime import datetime

# --- Configuration ---
BAUD = 115200
LOG_DIR = "logs/fuzzer_runs"
DEFAULT_PORT = "COM6"

def find_pico_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB Serial" in p.description or "2E8A" in p.hwid:
            return p.device
    return DEFAULT_PORT

def main():
    port = find_pico_port()
    
    print(f"--- UT33C+ Fuzzer Monitor ---")
    
    # Prompt for current mode to help with discovery
    current_mode = input("Enter current Multimeter Mode (e.g. 20V DC, Continuity, OFF): ").strip()
    if not current_mode: current_mode = "Unknown"
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"fuzzer_stream_{timestamp}.log")
    
    print(f"Monitoring: {port} @ {BAUD}")
    print(f"Current Mode: {current_mode}")
    print(f"Streaming to: {log_file}")
    print("Press Ctrl+C to stop.")
    print("-" * 40)

    try:
        with serial.Serial(port, BAUD, timeout=0.1) as ser:
            with open(log_file, "w") as f:
                f.write(f"# UT33C+ FUZZER SESSION START: {datetime.now().isoformat()}\n")
                f.write(f"# METER MODE: {current_mode}\n")
                f.write(f"# PORT: {port} | BAUD: {BAUD}\n\n")
                
                while True:
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8', errors='replace').strip()
                        if line:
                            now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            entry = f"[{now}] {line}"
                            
                            # Print to console
                            print(entry)
                            
                            # Write to log
                            f.write(entry + "\n")
                            f.flush()
                    
                    time.sleep(0.001) # High frequency polling
                    
    except KeyboardInterrupt:
        print(f"\nMonitoring stopped. Log saved to {log_file}")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()

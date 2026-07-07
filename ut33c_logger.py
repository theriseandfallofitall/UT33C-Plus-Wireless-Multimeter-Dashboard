#!/usr/bin/env python3
"""
UT33C+ Universal UART Logger (New Pads Edition)
Decodes the 2400 baud raw ADC stream from the internal UART pads.
Supports: Voltage, Current, Resistance, Continuity, Diode, and Temperature.
"""

import serial
import serial.tools.list_ports
import time
import csv
import os
from datetime import datetime

from ut33c.decoder import BAUD, decode_reading, pop_next_frame
from ut33c.ports import find_display_port


LOG_DIR = "logs"
CSV_FILE = f"ut33c_plus_log_{int(time.time())}.csv"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="UT33C+ Universal Logger")
    parser.add_argument("--port", help="Specific COM port to use (e.g. COM3). Auto-detects if omitted.", default=None)
    args = parser.parse_args()

    port = args.port or find_display_port()
    if not port:
        print("Error: No matching serial port found. Specify one with --port.")
        return

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_path = os.path.join(LOG_DIR, CSV_FILE)
    
    print(f"\n--- UT33C+ Universal Logger ---")
    print(f"Port: {port} | Baud: {BAUD}")
    print(f"Logging to: {log_path}")
    print("-" * 40)
    print(f"{'Time':12} | {'Mode':12} | {'Value':10} | {'Unit':6} | {'Raw Hex'}")
    print("-" * 40)

    try:
        with serial.Serial(port, BAUD, timeout=0.1) as ser:
            with open(log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Mode", "Value", "Unit", "Raw_Hex"])
                
                buffer = bytearray()
                while True:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        buffer.extend(data)

                        while True:
                            frame = pop_next_frame(buffer)
                            if frame is None:
                                break

                            mode, val, unit, _ = decode_reading(frame)
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            raw_hex = frame.hex(' ').upper()

                            print(f"{timestamp:12} | {mode:12} | {val:>10} | {unit:6} | {raw_hex}")
                            writer.writerow([datetime.now().isoformat(), mode, val, unit, raw_hex])
                            f.flush()
                    time.sleep(0.01)
                    
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()

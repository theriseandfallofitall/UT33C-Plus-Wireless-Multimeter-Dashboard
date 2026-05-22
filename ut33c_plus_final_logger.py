#!/usr/bin/env python3
"""
UT33C+ Universal UART Logger (New Pads Edition)
Decodes the 2400 baud raw ADC stream from the internal UART pads.
Supports: Voltage, Current, Resistance, Continuity, Diode, and Temperature.
"""

import serial
import serial.tools.list_ports
import time
import sys
import csv
import os
from datetime import datetime

# --- Configuration ---
BAUD = 2400
LOG_DIR = "logs"
CSV_FILE = f"ut33c_plus_log_{int(time.time())}.csv"

# --- Protocol Mapping ---
# Byte 3 (Range/Mode) Mapping
MODES = {
    0x0D: {"name": "20V DC", "unit": "V", "scale": 0.01, "offset": 0},
    0x0E: {"name": "20k Ohm", "unit": "kOhm", "scale": 0.01, "offset": 0},
    0x0F: {"name": "200mA DC", "unit": "mA", "scale": 0.1, "offset": 0},
    0x0B: {"name": "10A DC", "unit": "A", "scale": 0.01, "offset": 0},
    0x13: {"name": "Fahrenheit", "unit": "F", "scale": 1.0, "offset": 0},
    0x16: {"name": "Celsius", "unit": "C", "scale": 0.1, "offset": 0},
    0x17: {"name": "200mV DC", "unit": "mV", "scale": 0.1, "offset": -2000},
    0x19: {"name": "Cont/Diode", "unit": "counts", "scale": 1.0, "offset": 0},
    0x1A: {"name": "200k Ohm", "unit": "kOhm", "scale": 0.1, "offset": 0},
    0x1B: {"name": "20mA DC", "unit": "mA", "scale": 0.01, "offset": 0},
    0x1C: {"name": "2M Ohm", "unit": "MOhm", "scale": 0.001, "offset": 0},
    0x1E: {"name": "2000 Ohm", "unit": "Ohm", "scale": 1.0, "offset": 0},
    0x1F: {"name": "2000uA DC", "unit": "uA", "scale": 1.0, "offset": 0},
}

def checksum_ok(frame):
    if len(frame) != 10: return False
    # CS = sum(Bytes 2 to 8) & 0xFF
    return sum(frame[2:9]) & 0xFF == frame[9]

def decode_reading(frame):
    mode_byte = frame[3]
    # Reading is bytes 4,5,6,7. Usually 4-5 are high, 6-7 are low.
    # From our captures, 4-5 were 00 00 and 6-7 were the value.
    # We'll treat it as a 32-bit big-endian unsigned for safety.
    raw_val = int.from_bytes(frame[4:8], byteorder='big')
    
    if mode_byte in MODES:
        m = MODES[mode_byte]
        # Handle special OL state for these pads (7FFF or 0820)
        if raw_val >= 0x7FFF or (mode_byte == 0x17 and raw_val >= 2080):
            return m['name'], "OL", m['unit'], raw_val
        
        # Apply offset and scale
        val = (raw_val + m['offset']) * m['scale']
        return m['name'], f"{val:.2f}" if m['scale'] < 1 else f"{int(val)}", m['unit'], raw_val
    else:
        return f"Unknown ({hex(mode_byte)})", "???", "raw", raw_val

def find_port():
    ports = serial.tools.list_ports.comports()
    if not ports: return None
    # Prioritize USB Serial ports (likely the FTDI)
    for p in ports:
        if "USB" in p.description.upper() or "FT232" in p.description.upper():
            return p.device
    return ports[0].device

def main():
    port = find_port()
    if not port:
        print("Error: No serial ports found.")
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
                        
                        # Find frames starting with AB CD
                        while len(buffer) >= 10:
                            idx = buffer.find(b'\xAB\xCD')
                            if idx == -1:
                                buffer.clear()
                                break
                            if idx > 0:
                                del buffer[:idx]
                                continue
                            
                            # We have a candidate frame at index 0
                            frame = bytes(buffer[:10])
                            if checksum_ok(frame):
                                mode, val, unit, raw = decode_reading(frame)
                                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                raw_hex = frame.hex(' ').upper()
                                
                                # Print to console
                                print(f"{timestamp:12} | {mode:12} | {val:>10} | {unit:6} | {raw_hex}")
                                
                                # Log to CSV
                                writer.writerow([datetime.now().isoformat(), mode, val, unit, raw_hex])
                                f.flush()
                                
                                del buffer[:10]
                            else:
                                # Bad checksum, skip header and keep looking
                                del buffer[:2]
                    time.sleep(0.01)
                    
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()

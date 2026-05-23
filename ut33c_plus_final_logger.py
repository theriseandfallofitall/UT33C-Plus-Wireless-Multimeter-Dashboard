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
    0x13: {"name": "Fahrenheit", "unit": "°F", "scale": 1.0, "offset": 0, "transform": "celsius_to_fahrenheit"},
    0x16: {"name": "Celsius", "unit": "°C", "scale": 0.1, "offset": 0},
    0x17: {"name": "200mV DC", "unit": "mV", "scale": 0.1, "offset": 0}, # Offset removed, handled in logic
    0x19: {"name": "Continuity", "unit": "Ω", "scale": 1.0, "offset": 0, "transform": "continuity_diode"},
    0x1A: {"name": "200k Ohm", "unit": "kΩ", "scale": 0.1, "offset": 0},
    0x1B: {"name": "20mA DC", "unit": "mA", "scale": 0.01, "offset": 0},
    0x1C: {"name": "2M Ohm", "unit": "MΩ", "scale": 0.01, "offset": 0},
    0x1E: {"name": "2000 Ohm", "unit": "Ω", "scale": 1.0, "offset": 0},
    0x1F: {"name": "2000uA DC", "unit": "µA", "scale": 1.0, "offset": 0},
}

def celsius_to_fahrenheit(celsius_val):
    return (celsius_val * 9/5) + 32

def continuity_diode(raw_val):
    # Heuristic: 0x7F00 is confirmed "Open Loop" from logs
    if raw_val >= 0x7F00:
        return "OL", "Ω"
    # Diode mode shows voltage drop, typically < 3V
    if raw_val < 3000:
        return f"{raw_val / 1000.0:.3f}", "V"
    # Otherwise, it's resistance in Ohms for continuity
    return f"{raw_val}", "Ω"

def checksum_ok(frame):
    if len(frame) != 10: return False
    # CS = sum(Bytes 2 to 8) & 0xFF
    return sum(frame[2:9]) & 0xFF == frame[9]

def decode_reading(frame):
    mode_byte = frame[3]
    # We'll treat it as a 32-bit big-endian unsigned for safety.
    raw_val = int.from_bytes(frame[4:8], byteorder='big')
    
    if mode_byte in MODES:
        m = MODES[mode_byte]
        
        # Handle mode-specific OL conditions before any scaling
        # In 200mV mode, 2080 is the OL threshold
        if mode_byte == 0x17 and raw_val >= 2080:
            return m['name'], "OL", m['unit'], raw_val
        # For most resistance modes, a high value is OL
        if "Ohm" in m['name'] and raw_val >= 0x7F00:
             return m['name'], "OL", m['unit'], raw_val

        # Apply scaling and offset
        val = (raw_val + m.get('offset', 0)) * m.get('scale', 1.0)

        # Apply special transformations
        if m.get('transform') == 'celsius_to_fahrenheit':
            # Meter always sends Celsius; convert if in Fahrenheit mode
            celsius_val = (raw_val * 0.1) # Raw is C*10
            val = celsius_to_fahrenheit(celsius_val)
            return m['name'], f"{val:.1f}", m['unit'], raw_val
        
        if m.get('transform') == 'continuity_diode':
            new_val, new_unit = continuity_diode(raw_val)
            return m['name'], new_val, new_unit, raw_val

        # Format the final value
        # Determine decimal places based on scale
        if m['scale'] == 0.1:
            return m['name'], f"{val:.1f}", m['unit'], raw_val
        elif m['scale'] == 0.01:
            return m['name'], f"{val:.2f}", m['unit'], raw_val
        elif m['scale'] == 0.001:
            return m['name'], f"{val:.3f}", m['unit'], raw_val
        else:
            return m['name'], f"{int(val)}", m['unit'], raw_val
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

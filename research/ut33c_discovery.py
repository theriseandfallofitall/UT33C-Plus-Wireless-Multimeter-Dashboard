#!/usr/bin/env python3
"""UT33C+ UART Command Discovery Script
Tests various hex commands to see if the device responds to RX input.
"""
import serial
import time
import sys

BAUD = 2400

# Common UNI-T commands for meters using the AB-CD header format
# These often simulate button presses.
COMMANDS = [
    ("POLL DATA", "AB 00"),
    ("SELECT / REL", "AB 01"),
    ("RANGE", "AB 02"),
    ("MAX/MIN", "AB 03"),
    ("HOLD", "AB 06"),
    ("BACKLIGHT", "AB 07"),
    ("PEAK", "AB 05"),
    ("Hz/%", "AB 08"),
    # Extended 10-byte formats found in some bidirectional versions
    ("HOLD (10-byte)", "AB CD 01 01 01 00 00 00 00 03"), # CS is sum of 01..00
]

def send_command(ser, name, hex_str):
    cmd = bytes.fromhex(hex_str.replace(" ", ""))
    print(f"\n[TESTING] {name} ({hex_str})")
    
    # Clear buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Send
    ser.write(cmd)
    ser.flush()
    
    # Wait for response
    time.sleep(0.3)
    if ser.in_waiting:
        resp = ser.read(ser.in_waiting)
        print(f"  --> Response: {resp.hex(' ').upper()}")
        return True
    else:
        print("  --> No UART response.")
        return False

def main():
    port = "COM5"
    print(f"Opening {port} at {BAUD} baud...")
    
    try:
        with serial.Serial(port, BAUD, timeout=0.5) as ser:
            print("Successfully connected. Starting discovery...")
            print("NOTE: Watch the physical device screen for icon changes (HOLD, Light, etc.)")
            
            for name, hex_val in COMMANDS:
                send_command(ser, name, hex_val)
                time.sleep(1.0)
                
            print("\nDiscovery sequence complete.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

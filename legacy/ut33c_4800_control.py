#!/usr/bin/env python3
"""UT33C+ 4800 Baud Control Test
Tests if commands sent at 4800 baud trigger physical UI changes.
"""
import serial
import time

BAUD_RX = 4800
PORT = "COM5"

COMMANDS = [
    ("HOLD", "AB 06"),
    ("BACKLIGHT", "AB 07"),
    ("SELECT / REL", "AB 01"),
    ("RANGE", "AB 02"),
    ("MAX/MIN", "AB 03"),
    ("PEAK", "AB 05"),
    ("Hz/%", "AB 08"),
    ("POLL", "AB 00"),
]

def test_control():
    print(f"Starting 4800 baud control test on {PORT}...")
    print("Watch the meter for beeps, reboots, or screen changes.")
    
    try:
        with serial.Serial(PORT, BAUD_RX, timeout=0.1) as ser:
            for name, hex_str in COMMANDS:
                print(f"\n[SENDING] {name} ({hex_str})...")
                cmd = bytes.fromhex(hex_str)
                ser.write(cmd)
                ser.flush()
                
                # Wait longer to observe physical changes or reboots
                time.sleep(3.0)
                
            print("\nTest sequence complete.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_control()

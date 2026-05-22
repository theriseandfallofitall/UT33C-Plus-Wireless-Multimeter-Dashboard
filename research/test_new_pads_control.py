import serial
import time
import sys

# Protocol for control often matches the poll/button patterns
# AB 01: SELECT
# AB 02: RANGE
# AB 03: MAX/MIN
# AB 04: REL
# AB 06: HOLD
# AB 07: LIGHT
COMMANDS = [
    ("SELECT", "AB 01"),
    ("RANGE", "AB 02"),
    ("HOLD", "AB 06"),
    ("LIGHT", "AB 07"),
]

def test_control(port, baud=2400):
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            print(f"Connected to {port} at {baud} baud.")
            print("Listening for 2 seconds to confirm data flow...")
            
            # Initial listen
            start = time.time()
            while time.time() - start < 2:
                if ser.in_waiting:
                    ser.read(ser.in_waiting)
                time.sleep(0.01)
            
            for name, hex_cmd in COMMANDS:
                print(f"\n[SENDING] {name} ({hex_cmd})...")
                cmd = bytes.fromhex(hex_cmd)
                ser.write(cmd)
                ser.flush()
                
                # Check for immediate response or screen change
                print("Checking for changes in stream (3s)...")
                start = time.time()
                while time.time() - start < 3:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        print(f"  RECV: {data.hex(' ').upper()}")
                    time.sleep(0.05)
                
                input("Press Enter for next command (Check meter screen!)...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_control("COM5")

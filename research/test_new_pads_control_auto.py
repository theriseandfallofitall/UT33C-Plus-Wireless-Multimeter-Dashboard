import serial
import time
import sys

# Common UNI-T command patterns
COMMANDS = [
    ("SELECT", "AB 01"),
    ("RANGE", "AB 02"),
    ("HOLD", "AB 06"),
    ("LIGHT", "AB 07"),
]

def test_control_auto(port, baud=2400):
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            print(f"Connected to {port} at {baud} baud.")
            print("Warming up (2s)...")
            time.sleep(2)
            
            for name, hex_cmd in COMMANDS:
                print(f"\n[SENDING] {name} ({hex_cmd})...")
                cmd = bytes.fromhex(hex_cmd)
                ser.write(cmd)
                ser.flush()
                
                # Check for response/changes for 5 seconds
                start = time.time()
                while time.time() - start < 5:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        # Filter out the standard 10-byte frames to see if anything NEW appears
                        # Standard frames start with AB CD. If we see something else, it's a response.
                        print(f"  RECV: {data.hex(' ').upper()}")
                    time.sleep(0.1)
                
                print(f"Finished testing {name}. Moving to next...")

            print("\nAutomated test sequence complete.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_control_auto("COM5")

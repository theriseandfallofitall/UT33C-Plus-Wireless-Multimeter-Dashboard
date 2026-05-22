import serial
import time
import sys

port = "COM5"
cmd_hex = "AB 06" # HOLD command

def test_baud_interactive(baud):
    print(f"\nTesting {baud} baud...")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            cmd = bytes.fromhex(cmd_hex)
            print(f"  Sending {cmd_hex} at {baud} baud...")
            ser.write(cmd)
            ser.flush()
            time.sleep(0.2)
    except Exception as e:
        print(f"  Error: {e}")
    
    input("  Did it beep? (Press Enter for next baud)")

if __name__ == "__main__":
    for b in [2400, 4800, 9600, 19200]:
        test_baud_interactive(b)

import serial
import time
import sys

# Characters often used to enter bootloaders or test modes
ENTRY_CHARS = [b'Q', b'P', b' ', b'\x03', b'\xAB', b'\x55', b'\xAA']

def pulse_reset_and_sync(port, baud=2400):
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            for char in ENTRY_CHARS:
                print(f"\n--- Testing Entry Char: {char} ---")
                
                # Pulse Reset
                ser.dtr = True
                ser.rts = True
                time.sleep(0.2)
                ser.dtr = False
                ser.rts = False
                
                # Immediately blast the char for 1 second
                start = time.time()
                while time.time() - start < 1.0:
                    ser.write(char)
                    time.sleep(0.01)
                
                # Check for response
                print("  Listening...")
                start = time.time()
                while time.time() - start < 2:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        print(f"  RECV: {data.hex(' ').upper()}")
                    time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pulse_reset_and_sync("COM5")

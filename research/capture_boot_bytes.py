import serial
import time
import sys

def capture_boot_bytes(port, baud=2400):
    print(f"Monitoring {port} for ANY non-standard frames...")
    print(">>> GROUND PAD 2 NOW! <<<")
    
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            buffer = bytearray()
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # If it's not the start of a standard frame, print it
                    if not data.startswith(b'\xAB\xCD'):
                        print(f"DEBUG: {data.hex(' ').upper()}")
                    else:
                        # Print only the first few bytes of standard frames to keep it clean
                        print(f"DATA: {data[:4].hex(' ').upper()}...")
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_boot_bytes("COM5")

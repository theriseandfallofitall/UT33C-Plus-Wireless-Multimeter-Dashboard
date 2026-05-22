import serial
import time
import sys

def blast_on_reset_signature(port, baud=2400):
    print(f"Monitoring {port} for reset signature at {baud} baud...")
    print(">>> PULSE RESET NOW! <<<")
    
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # Detect the signature bytes we saw earlier (01 00 00 81)
                    if any(b in data for b in [0x01, 0x81]):
                        print(f"  [SIGNATURE DETECTED]: {data.hex(' ').upper()}")
                        print("  !!! BLASTING SELECT COMMAND !!!")
                        # Blast for 0.5 seconds
                        start = time.time()
                        while time.time() - start < 0.5:
                            ser.write(bytes.fromhex("AB 01"))
                            time.sleep(0.01)
                        print("  Done. Monitoring for mode change...")
                        
                time.sleep(0.005)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    blast_on_reset_signature("COM5")

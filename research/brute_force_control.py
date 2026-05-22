import serial
import time
import sys

def brute_force_control(port, baud=2400):
    print(f"Brute-forcing commands on {port}...")
    print(">>> GROUND PAD 2 NOW AND RELEASE! <<<")
    
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            # We will cycle through AB 00 to AB 1F (common button/mode codes)
            # and blast them repeatedly.
            cmds = [bytes([0xAB, i]) for i in range(32)]
            
            start_time = time.time()
            count = 0
            while time.time() - start_time < 30: # Run for 30 seconds
                for cmd in cmds:
                    ser.write(cmd)
                    # No sleep here, we want maximum density
                    
                count += 1
                if count % 100 == 0:
                    print(f"Blasted {count} full command sets...")
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        # Just print snippets to see if it's still alive
                        print(f"  [RECV Snippet]: {data[:10].hex(' ').upper()}")

    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    brute_force_control("COM5")

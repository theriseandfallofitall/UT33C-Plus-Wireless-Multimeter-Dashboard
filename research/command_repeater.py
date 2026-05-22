import serial
import time
import sys

def command_repeater(port, baud=2400):
    cmd = bytes.fromhex("AB 01") # SELECT command
    print(f"Repeating SELECT command on {port} at {baud} baud...")
    print(">>> TRY GROUNDING PAD 1 OR PAD 2 WHILE THIS RUNS <<<")
    print("Watch the meter for mode changes or icons!")
    
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            count = 0
            while True:
                ser.write(cmd)
                ser.flush()
                count += 1
                if count % 10 == 0:
                    print(f"Sent {count} commands...")
                
                # Check for any unexpected return data
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    if b'\xAB\xCD' not in data:
                        print(f"  [UNIQUE RECV]: {data.hex(' ').upper()}")
                
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    command_repeater("COM5")

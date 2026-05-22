import serial
import time
import sys

def monitor_with_breaks(port, baud=2400):
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            print("Monitoring... (Steady State)")
            start = time.time()
            while time.time() - start < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"RECV: {data.hex(' ').upper()}")
                time.sleep(0.05)
            
            print("\n>>> APPLYING BREAK (Pulling RX LOW) <<<")
            # Pull low for 3 seconds
            ser.break_condition = True
            start = time.time()
            while time.time() - start < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"RECV during Break: {data.hex(' ').upper()}")
                time.sleep(0.05)
            
            print("\n>>> RELEASING BREAK <<<")
            ser.break_condition = False
            start = time.time()
            while time.time() - start < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"RECV after Break: {data.hex(' ').upper()}")
                time.sleep(0.05)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_with_breaks("COM5")

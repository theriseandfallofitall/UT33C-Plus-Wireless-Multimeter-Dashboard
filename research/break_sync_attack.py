import serial
import time
import sys

def break_sync_attack(port, baud=2400):
    print(f"Starting Break-Sync attack on {port}...")
    print(">>> GROUND PAD 2 NOW! <<<")
    
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            # 1. Apply Break (Pull RX LOW)
            ser.break_condition = True
            print("  Break applied (RX LOW). waiting for reset pulse...")
            
            # Keep break for 5 seconds to give user time
            time.sleep(5)
            
            # 2. Release Break
            ser.break_condition = False
            print("  Break released. Blasting Sync...")
            
            # 3. Blast Sync Characters
            start = time.time()
            while time.time() - start < 2:
                ser.write(b'\x55\xAA\xAB\x01')
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    if data:
                        print(f"  [RECV]: {data.hex(' ').upper()}")
                time.sleep(0.01)
            
            print("\nMonitoring for results (5s)...")
            start = time.time()
            while time.time() - start < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  [RECV]: {data.hex(' ').upper()}")
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    break_sync_attack("COM5")

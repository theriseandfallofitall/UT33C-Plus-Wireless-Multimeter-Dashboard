import serial
import time
import sys

def monitor_reset(port, baud=2400, duration=10):
    print(f"Monitoring {port} at {baud} baud for {duration}s...")
    print(">>> PLEASE PULSE THE RESET PIN NOW <<<")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            start_time = time.time()
            while time.time() - start_time < duration:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # Use a timestamp to see exactly when data stops/starts
                    ts = time.time() - start_time
                    print(f"[{ts:6.3f}s] RECV: {data.hex(' ').upper()}")
                time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_reset("COM5")

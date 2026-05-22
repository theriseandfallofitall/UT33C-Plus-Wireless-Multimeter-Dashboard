import serial
import time

def capture(port, baud, duration=5):
    print(f"Capturing on {port} at {baud} baud for {duration}s...")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            start_time = time.time()
            while time.time() - start_time < duration:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    if data:
                        print(f"RECV: {data.hex(' ').upper()}")
                time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture("COM5", 2400)

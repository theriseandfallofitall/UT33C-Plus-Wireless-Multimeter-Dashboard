import serial
import time

port = "COM5"
baud = 2400

print(f"Waiting for {port} to become available...")
ser = None
for _ in range(10):
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        print("Connected!")
        break
    except serial.SerialException:
        time.sleep(0.5)

if ser:
    try:
        print("Listening for data (Raw Hex)...")
        start = time.time()
        while time.time() - start < 15:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(data.hex(' ').upper(), end=' ', flush=True)
            time.sleep(0.01)
    finally:
        ser.close()
else:
    print("Failed to open port after retries.")

import serial
import time
import sys

port = "COM5"
baud = 2400

try:
    ser = serial.Serial(port, baud, timeout=0.1)
    print("Connected!")
    while True:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            print(data.hex(' ').upper(), end=' ', flush=True)
        time.sleep(0.01)
except Exception as e:
    print(f"Error: {e}")

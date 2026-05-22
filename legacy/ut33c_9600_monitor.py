import serial
import time

port = "COM5"

def monitor_9600():
    print(f"Monitoring {port} at 9600 baud...")
    try:
        with serial.Serial(port, 9600, timeout=0.1) as ser:
            print("Resetting meter...")
            ser.dtr = True
            ser.rts = True
            time.sleep(0.2)
            ser.dtr = False
            ser.rts = False
            time.sleep(0.5)
            
            print("Listening...")
            start = time.time()
            while time.time() - start < 10:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"[{time.strftime('%H:%M:%S')}] {data.hex(' ').upper()}")
                time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_9600()

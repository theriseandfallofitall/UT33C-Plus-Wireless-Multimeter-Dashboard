import serial
import time
import sys

def listen(port, baud, duration=5):
    print(f"\n--- Listening on {port} at {baud} baud for {duration}s ---")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            start_time = time.time()
            while time.time() - start_time < duration:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"[{time.strftime('%H:%M:%S')}] RECV: {data.hex(' ').upper()}")
                time.sleep(0.01)
    except Exception as e:
        print(f"Error on {port} at {baud}: {e}")

def poll(port, baud):
    print(f"\n--- Polling on {port} at {baud} baud ---")
    try:
        with serial.Serial(port, baud, timeout=0.5) as ser:
            cmd = bytes.fromhex("AB 00")
            print(f"SEND: {cmd.hex(' ').upper()}")
            ser.write(cmd)
            ser.flush()
            time.sleep(0.5)
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(f"RECV: {data.hex(' ').upper()}")
            else:
                print("No response to poll.")
    except Exception as e:
        print(f"Error polling on {port} at {baud}: {e}")

if __name__ == "__main__":
    port = "COM5"
    # First just listen
    for baud in [2400, 4800, 9600]:
        listen(port, baud, duration=3)
    
    # Then try polling
    for baud in [2400, 4800, 9600]:
        poll(port, baud)

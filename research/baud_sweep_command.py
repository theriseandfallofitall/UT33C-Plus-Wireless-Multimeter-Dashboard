import serial
import time
import sys

def baud_sweep_command(port):
    bauds = [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    cmd = bytes.fromhex("AB 01")
    print(f"Baud Sweep Command on {port}...")
    
    for b in bauds:
        print(f"\nTesting {b} baud...")
        try:
            with serial.Serial(port, b, timeout=0.1) as ser:
                for _ in range(5):
                    ser.write(cmd)
                    ser.flush()
                    time.sleep(0.1)
                
                # Check for any response
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  [RECV at {b}]: {data.hex(' ').upper()}")
                else:
                    print(f"  No response at {b}.")
        except Exception as e:
            print(f"  Error at {b}: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    baud_sweep_command("COM5")

import serial
import time
import sys

def monitor_bootloop(port, baud=9600, duration=15):
    print(f"Monitoring {port} at {baud} baud for {duration}s...")
    print(">>> METER IS IN BOOT LOOP - CAPTURING DIAGNOSTICS <<<")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            start_time = time.time()
            while time.time() - start_time < duration:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    ts = time.time() - start_time
                    # Print both hex and ASCII in case it's a text-based bootloader
                    hex_data = data.hex(' ').upper()
                    ascii_data = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in data])
                    print(f"[{ts:6.3f}s] HEX: {hex_data} | ASCII: {ascii_data}")
                time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_bootloop("COM5")

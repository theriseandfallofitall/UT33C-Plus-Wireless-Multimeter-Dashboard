import serial
import time
import sys

def monitor_beep_event(port, baud=2400, duration=10):
    print(f"Monitoring {port} at {baud} baud for {duration}s...")
    print(">>> PULSE RESET NOW AND WATCH FOR THE LONG BEEP <<<")
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            start_time = time.time()
            while time.time() - start_time < duration:
                if ser.in_waiting:
                    # Read all available data to preserve timing
                    data = ser.read(ser.in_waiting)
                    ts = time.time() - start_time
                    hex_val = data.hex(' ').upper()
                    
                    # Look for the signature bytes we saw before
                    if any(b in data for b in [0x81, 0x01, 0x00]) and b'\xAB\xCD' not in data:
                        print(f"[{ts:6.3f}s] !!! SIGNATURE DETECTED: {hex_val}")
                    else:
                        print(f"[{ts:6.3f}s] RECV: {hex_val}")
                time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_beep_event("COM5")

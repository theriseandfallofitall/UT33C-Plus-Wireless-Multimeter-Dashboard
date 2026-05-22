import serial
import time

port = "COM5"

def monitor_ncv_mode():
    print(f"Monitoring {port} at 2400 baud...")
    print("ACTION: Trigger the Lightning Bolt mode (PAD2 High + Reset).")
    print("Watching for NCV/EF (Electric Field) data packets...")
    
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            ser.reset_input_buffer()
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    hx = data.hex(' ').upper()
                    # Look for Mode changes. Normal is 0x01.
                    # NCV often uses a different Mode byte or a unique 10-byte frame.
                    print(f"[{time.strftime('%H:%M:%S')}] {hx}")
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_ncv_mode()

import serial
import time

port = "COM5"

def capture_glitch_state():
    print(f"Monitoring {port} for data after glitch...")
    print("ACTION: Perform the high-frequency reset pulsing to trigger the long beep.")
    
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            ser.reset_input_buffer()
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # Use time.perf_counter for high precision timing between chunks
                    ts = time.strftime('%H:%M:%S')
                    print(f"[{ts}] {data.hex(' ').upper()}")
                time.sleep(0.001)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_glitch_state()

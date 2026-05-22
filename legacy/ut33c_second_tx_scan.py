import serial
import time

port = "COM5"

def scan_new_tx(port):
    # Testing common baud rates for this second TX line
    for baud in [2400, 4800, 9600, 19200]:
        print(f"\n--- Testing Second TX at {baud} baud ---")
        print(f"Watching for 5 seconds...")
        try:
            with serial.Serial(port, baud, timeout=0.1) as ser:
                ser.reset_input_buffer()
                start = time.time()
                while time.time() - start < 5:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        print(f"[{time.strftime('%H:%M:%S')}] {data.hex(' ').upper()}")
                    time.sleep(0.01)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("ACTION: Connect your FTDI RX wire to the NEW pad (next to the original TX).")
    input("Press Enter when connected...")
    scan_new_tx(port)

import serial
import time

def test_baud(port, baud):
    print(f"\nTesting RX at {baud} baud...")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            cmd = bytes.fromhex("AB 06")
            ser.write(cmd)
            ser.flush()
            time.sleep(0.5)
            # Switch back to 2400 to read response
    except serial.SerialException:
        return

    try:
        with serial.Serial(port, 2400, timeout=0.5) as ser:
            if ser.in_waiting:
                resp = ser.read(ser.in_waiting)
                print(f"  Response (at 2400): {resp.hex(' ').upper()}")
            else:
                print("  No response.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = "COM5"
    for b in [2400, 4800, 9600, 19200]:
        test_baud(port, b)

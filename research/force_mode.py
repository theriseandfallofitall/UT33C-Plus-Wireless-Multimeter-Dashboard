import serial
import time
import sys

def calc_cs(frame):
    return sum(frame[2:9]) & 0xFF

def send_force_mode(port, mode_byte, range_byte):
    print(f"Attempting to FORCE Mode: 0x{mode_byte:02X}, Range: 0x{range_byte:02X}")
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            # Construct a frame that mirrors what the meter sends
            frame = bytearray([0xAB, 0xCD, mode_byte, range_byte, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            frame[9] = calc_cs(frame)
            
            print(f"  Sending: {frame.hex(' ').upper()}")
            for _ in range(20):
                ser.write(frame)
                ser.flush()
                time.sleep(0.1)
                
            # Now listen for a few seconds
            print("  Listening for feedback...")
            start = time.time()
            while time.time() - start < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  RECV: {data.hex(' ').upper()}")
                time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = "COM5"
    # Try forcing into 2000 Ohm mode (1E)
    send_force_mode(port, 0x01, 0x1E)
    # Try forcing into Celsius mode (16)
    send_force_mode(port, 0x01, 0x16)

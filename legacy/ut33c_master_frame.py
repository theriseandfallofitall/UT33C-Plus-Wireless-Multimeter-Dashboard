import serial
import time

def calculate_checksum(data):
    # Sum of bytes 2 through 8
    return sum(data[2:9]) & 0xFF

def send_master_frame(port, mode, range_id, b0=0, b1=0, b2=0, b3=0, b4=0):
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            frame = bytearray([0xAB, 0xCD, mode, range_id, b0, b1, b2, b3, b4, 0x00])
            frame[9] = calculate_checksum(frame)
            
            print(f"Sending Master Frame: {frame.hex(' ').upper()}")
            ser.write(frame)
            ser.flush()
            
            time.sleep(0.5)
            if ser.in_waiting:
                resp = ser.read(ser.in_waiting)
                print(f"Response: {resp.hex(' ').upper()}")
            else:
                print("No response.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = "COM5"
    # Try a control command (Mode 00 instead of 01)
    # 0x06 is often "Hold" in these protocols
    print("--- Test 1: Mode 0x00, Command 0x06 (HOLD) ---")
    send_master_frame(port, 0x00, 0x06)
    
    print("\n--- Test 2: Mode 0x01 (Mirroring meter's own mode), Command 0x06 ---")
    send_master_frame(port, 0x01, 0x06)

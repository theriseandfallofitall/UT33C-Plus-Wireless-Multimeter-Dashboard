import serial
import time
import sys

def calc_cs(data_bytes):
    # Sum bytes from index 2 to 8 (MODE to B4)
    return sum(data_bytes[2:9]) & 0xFF

def make_10byte_cmd(mode, range_val=0, b0=0, b1=0, b2=0, b3=0, b4=0):
    cmd = [0xAB, 0xCD, mode, range_val, b0, b1, b2, b3, b4, 0x00]
    cmd[9] = calc_cs(cmd)
    return bytes(cmd)

# Construct a set of 10-byte commands to test
COMMANDS_10B = [
    ("POLL", make_10byte_cmd(0x00)),
    ("SELECT", make_10byte_cmd(0x01)),
    ("RANGE", make_10byte_cmd(0x02)),
    ("HOLD", make_10byte_cmd(0x06)),
    ("LIGHT", make_10byte_cmd(0x07)),
    ("ALT_POLL", bytes.fromhex("AB CD 01 01 01 00 00 00 00 03")),
]

def pulse_reset(ser):
    print(">>> PULSING RESET (DTR/RTS) <<<")
    ser.dtr = True
    ser.rts = True
    time.sleep(0.2)
    ser.dtr = False
    ser.rts = False

def blast_10byte(port, baud=2400, cycles=5):
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            print(f"Connected to {port} at {baud} baud.")
            
            for i in range(cycles):
                print(f"\n--- 10-Byte Cycle {i+1}/{cycles} ---")
                pulse_reset(ser)
                
                print("Blasting 10-byte commands...")
                start_time = time.time()
                while time.time() - start_time < 2.5:
                    for name, cmd in COMMANDS_10B:
                        ser.write(cmd)
                    
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        # Filter to see if we get anything OTHER than the usual AB CD frames
                        if data[0:2] != b'\xAB\xCD' or len(data) != 10:
                            print(f"  [UNIQUE RECV]: {data.hex(' ').upper()}")
                    time.sleep(0.05)
                
                print("Monitoring (3s)...")
                start_time = time.time()
                while time.time() - start_time < 3:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        print(f"  [RECV]: {data.hex(' ').upper()}")
                    time.sleep(0.1)

            print("\n10-Byte Blast sequence complete.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    blast_10byte("COM5")

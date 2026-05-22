#!/usr/bin/env python3
import serial
import time

BAUD = 2400
PORT = "COM5"

def test_select_variants(port):
    variants = [
        ("Standard SELECT", "AB 01"),
        ("10-byte SELECT (CS=03)", "AB CD 01 01 01 00 00 00 00 03"),
        ("3-byte Variant", "AB 00 01"),
        ("Query/Toggle 'Q'", "51"),
    ]
    
    try:
        with serial.Serial(port, BAUD, timeout=0.1) as ser:
            for name, hex_str in variants:
                print(f"\n" + "="*40)
                print(f"TESTING: {name} ({hex_str})")
                print("Watch for the 'Diode' vs 'Buzzer' icon changing!")
                print("="*40)
                
                ser.reset_input_buffer()
                cmd = bytes.fromhex(hex_str.replace(" ", ""))
                ser.write(cmd)
                ser.flush()
                
                start_time = time.time()
                while time.time() - start_time < 5:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        # Look for Byte 3 (Mode) or Byte 8 (Status) changes
                        print(f"[{time.strftime('%H:%M:%S')}] RECV: {data.hex(' ').upper()}")
                    time.sleep(0.1)
                
                time.sleep(1) # Pause between variants
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_select_variants(PORT)

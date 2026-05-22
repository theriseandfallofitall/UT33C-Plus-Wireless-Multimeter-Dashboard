#!/usr/bin/env python3
import serial
import time
import sys

def test_command(port, cmd_hex, name):
    print(f"\n" + "="*40)
    print(f"TESTING: {name} ({cmd_hex})")
    print(f"Watch the meter screen for 5 seconds!")
    print("="*40)
    
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            ser.reset_input_buffer()
            # Send command
            cmd = bytes.fromhex(cmd_hex)
            ser.write(cmd)
            ser.flush()
            
            start_time = time.time()
            while time.time() - start_time < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # Try to find a frame in the data to show status
                    print(f"[{time.strftime('%H:%M:%S')}] RECV: {data.hex(' ').upper()}")
                time.sleep(0.1)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = "COM5"
    
    # 1. Test Backlight
    test_command(port, "AB 07", "BACKLIGHT TOGGLE")
    
    print("\nPausing for 2 seconds...")
    time.sleep(2)
    
    # 2. Test Select (REL/Mode)
    test_command(port, "AB 01", "SELECT / REL")

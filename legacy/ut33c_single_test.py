#!/usr/bin/env python3
import serial
import time

def test_single_command(port, cmd_hex, name):
    print(f"\n--- Testing: {name} ({cmd_hex}) ---")
    print("Watching for 5 seconds. Look at the meter for decimal moves or icon changes.")
    
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            # Send command
            cmd = bytes.fromhex(cmd_hex)
            ser.write(cmd)
            ser.flush()
            
            start_time = time.time()
            while time.time() - start_time < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"[{time.strftime('%H:%M:%S')}] UART RECV: {data.hex(' ').upper()}")
                time.sleep(0.05)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test RANGE (AB 02) as it caused a response before
    test_single_command("COM5", "AB 02", "RANGE CYCLE")

import serial
import time
import sys

def test_hardware_signals(port, baud=2400):
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            print(f"Testing hardware signals on {port}...")
            
            # 1. Pull RX (TX from FTDI) LOW for 2 seconds
            print("\nStep 1: Pulling RX LOW (Break) for 2s...")
            ser.send_break(duration=2)
            time.sleep(0.5)
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(f"  RECV after Break: {data.hex(' ').upper()}")
            
            # 2. Pull RX HIGH (Standard idle) and monitor
            print("\nStep 2: Monitoring steady state...")
            start = time.time()
            while time.time() - start < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  RECV: {data.hex(' ').upper()}")
                time.sleep(0.1)
                
            # 3. Fast Pulsing (Simulate Clock)
            print("\nStep 3: Fast pulsing RX...")
            for _ in range(100):
                ser.write(b'\x00') # Zero bytes cause transitions
            time.sleep(0.5)
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(f"  RECV after pulsing: {data.hex(' ').upper()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hardware_signals("COM5")

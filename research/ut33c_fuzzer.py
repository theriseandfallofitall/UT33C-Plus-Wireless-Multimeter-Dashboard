#!/usr/bin/env python3
import serial
import time
import sys

BAUD = 2400
PORT = "COM5"

def test_off_state(port):
    print("\n" + "="*40)
    print("PHASE 1: OFF-STATE MONITORING")
    print("Ensuring the meter is in the OFF position.")
    print("="*40)
    
    try:
        with serial.Serial(port, BAUD, timeout=1) as ser:
            print("Listening for 5 seconds for any 'heartbeat'...")
            start = time.time()
            while time.time() - start < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"RECV: {data.hex(' ').upper()}")
                time.sleep(0.1)
            
            print("\nAttempting to 'Wake' with trigger bytes...")
            for b in [0x00, 0x51, 0xAB, 0xFF]:
                print(f"Sending {hex(b)}...")
                ser.write(bytes([b]))
                ser.flush()
                time.sleep(0.5)
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  !! RESPONSE: {data.hex(' ').upper()}")
                else:
                    print("  No response.")

    except Exception as e:
        print(f"Error: {e}")

def fuzz_1byte(port):
    print("\n" + "="*40)
    print("PHASE 2: 1-BYTE FUZZING (0x00 - 0xFF)")
    print("Please turn the meter ON to any range (e.g., 20V DC).")
    print("="*40)
    input("Press Enter when the meter is back ON...")

    results = {}
    try:
        with serial.Serial(port, BAUD, timeout=0.2) as ser:
            for i in range(256):
                if i % 16 == 0:
                    print(f"Fuzzing range: {hex(i)} - {hex(i+15)}...")
                
                ser.reset_input_buffer()
                ser.write(bytes([i]))
                ser.flush()
                
                time.sleep(0.15)
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # Store unique responses (length or content)
                    resp_hex = data.hex(' ').upper()
                    if resp_hex not in results:
                        results[resp_hex] = [hex(i)]
                    else:
                        results[resp_hex].append(hex(i))
            
            print("\n" + "="*40)
            print("FUZZING RESULTS (Unique Responses)")
            print("="*40)
            for resp, triggers in results.items():
                print(f"Triggers {triggers} -> {resp[:50]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_off_state(PORT)
    fuzz_1byte(PORT)

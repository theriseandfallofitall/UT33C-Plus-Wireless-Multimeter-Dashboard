#!/usr/bin/env python3
"""UT33C+ UART Handshake/Diagnostic Discovery
Tests various common wake-up and diagnostic bytes used by UNI-T and Fortune ICs.
"""
import serial
import time

BAUD = 2400

# Common diagnostic/handshake sequences
HANDSHAKES = [
    ("ASCII 'Q' (Query)", "51"),
    ("ASCII 'AT' (Wakeup)", "41 54"),
    ("Hex 0x05 (ENQ)", "05"),
    ("Hex 0x11 (XON)", "11"),
    ("Diagnostic Start", "55 AA 01 01"),
    ("Calibration Entry", "AE AE 55 AA"),
    ("Null Byte", "00"),
]

def test_handshake(port, name, hex_str):
    print(f"\n[HANDSHAKE] {name} ({hex_str})")
    try:
        with serial.Serial(port, BAUD, timeout=0.1) as ser:
            ser.reset_input_buffer()
            cmd = bytes.fromhex(hex_str.replace(" ", ""))
            ser.write(cmd)
            ser.flush()
            
            # Watch for a change in frame structure or a unique response
            start_time = time.time()
            while time.time() - start_time < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # We look for anything that DOES NOT start with AB CD
                    # or has a different length/content.
                    print(f"  --> RECV: {data.hex(' ').upper()}")
                time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = "COM5"
    print(f"Starting handshake discovery on {port}...")
    for name, hex_val in HANDSHAKES:
        test_handshake(port, name, hex_val)
    print("\nDiscovery finished.")

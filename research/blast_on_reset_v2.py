import serial
import time
import sys

# Protocol for control often matches the poll/button patterns
# AB 01: SELECT
# AB 02: RANGE
# AB 06: HOLD
# AB 07: LIGHT
COMMAND = bytes.fromhex("AB 01") 

def blast_on_pad2_reset(port, baud=2400):
    print(f"Monitoring {port} for Pad 2 Hard Reset signature...")
    print(">>> GROUND PAD 2 NOW! <<<")
    
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            buffer = bytearray()
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    buffer.extend(data)
                    
                    # Keep buffer small
                    if len(buffer) > 50:
                        buffer = buffer[-50:]
                    
                    # Look for the Hard Reset signature: 01 00 00 81
                    # (Seen in previous Pad 2 monitor runs)
                    if b'\x01\x00\x00\x81' in buffer:
                        print(f"\n[!!! BOOT SIGNATURE DETECTED !!!]")
                        print("  Blasting SELECT command for 2 seconds...")
                        
                        start_blast = time.time()
                        while time.time() - start_blast < 2.0:
                            ser.write(COMMAND)
                            # Small sleep to not overflow the meter's tiny RX buffer
                            time.sleep(0.02)
                        
                        print("  Blast complete. Checking for mode change...")
                        buffer.clear()
                        
                        # Monitor return for 5 seconds
                        monitor_start = time.time()
                        while time.time() - monitor_start < 5:
                            if ser.in_waiting:
                                resp = ser.read(ser.in_waiting)
                                if b'\xAB\xCD' in resp:
                                    # Extract the range byte (index 3 of a 10-byte frame)
                                    # This is a bit simplified but good for a quick check
                                    print(f"  RECV Data: {resp.hex(' ').upper()}")
                            time.sleep(0.1)
                        
                        print("\n>>> READY FOR NEXT RESET <<<")

                time.sleep(0.005)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    blast_on_pad2_reset("COM5")

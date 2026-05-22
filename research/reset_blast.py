import serial
import time
import sys

# Commands to try during the "blast"
COMMANDS = [
    bytes.fromhex("AB 00"), # Poll
    bytes.fromhex("AB 01"), # Select
    bytes.fromhex("AB CD 01 01 01 00 00 00 00 03"), # 10-byte poll
    bytes.fromhex("55 AA"), # Common bootloader sync
    bytes.fromhex("7F"),    # STM32 bootloader sync
]

def pulse_reset(ser):
    print(">>> PULSING RESET (DTR/RTS) <<<")
    ser.dtr = True
    ser.rts = True
    time.sleep(0.2)
    ser.dtr = False
    ser.rts = False

def blast_and_monitor(port, baud=2400, cycles=5):
    try:
        with serial.Serial(port, baud, timeout=0.01) as ser:
            print(f"Connected to {port} at {baud} baud.")
            
            for i in range(cycles):
                print(f"\n--- Cycle {i+1}/{cycles} ---")
                pulse_reset(ser)
                
                print("Blasting commands...")
                start_time = time.time()
                # Blast for 2 seconds immediately after reset
                while time.time() - start_time < 2:
                    for cmd in COMMANDS:
                        ser.write(cmd)
                    
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        print(f"  [RECV]: {data.hex(' ').upper()}")
                    time.sleep(0.05)
                
                print("Monitoring for steady-state (3s)...")
                start_time = time.time()
                while time.time() - start_time < 3:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                        print(f"  [RECV]: {data.hex(' ').upper()}")
                    time.sleep(0.1)

            print("\nBlast sequence complete.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure COM5 is available
    blast_and_monitor("COM5")

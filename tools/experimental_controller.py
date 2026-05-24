#!/usr/bin/env python3
"""
UT33C+ Experimental Controller
-------------------------------
Sends commands to the UT33C+ via its internal UART pads.

**WARNING:** Based on extensive testing, the RX line on the internal pads
appears to be disabled or ignored by the multimeter's firmware. This script
is provided for research purposes to further test this hypothesis, but it is
not expected to successfully control the meter.

The commands are based on protocols from other UNI-T devices, as the UT33C+
protocol is not publicly documented.
"""
import serial
import serial.tools.list_ports
import time
import argparse

# Known commands from other UNI-T devices that might be relevant.
# The structure is typically [Header] [Command] [Checksum].
COMMANDS = {
    "SELECT_BUTTON": b'\xAB\x01\xAC', # Simulates the 'SELECT' button
    "RANGE_BUTTON":  b'\xAB\x02\xAD', # Simulates the 'RANGE' button
    "REL_BUTTON":    b'\xAB\x03\xAE', # Simulates the 'REL' button
    "HOLD_BUTTON":   b'\xAB\x04\xAF', # Simulates the 'HOLD' button
}

def find_port():
    """Find and select a serial port."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("Error: No serial ports found.")
        return None
    
    print("\nAvailable Serial Ports:")
    for i, p in enumerate(ports):
        print(f"[{i}] {p.device} ({p.description})")
    
    while True:
        try:
            choice = int(input(f"Select port [0-{len(ports)-1}]: "))
            if 0 <= choice < len(ports):
                return ports[choice].device
        except (ValueError, IndexError):
            print("Invalid selection.")

def main():
    parser = argparse.ArgumentParser(description="UT33C+ Experimental Controller")
    parser.add_argument("--port", help="Serial port to use (e.g., COM5 or /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=2400, help="Baud rate for communication")
    args = parser.parse_args()

    port = args.port or find_port()
    if not port:
        return

    print("\n--- UT33C+ Experimental Controller ---")
    print("WARNING: This is for research only. The meter is not expected to respond.")
    print(f"Using port: {port} at {args.baud} baud")
    
    print("\nAvailable commands:")
    for i, name in enumerate(COMMANDS.keys()):
        print(f"[{i}] {name}")

    try:
        with serial.Serial(port, args.baud, timeout=1) as ser:
            while True:
                try:
                    cmd_choice = input("\nEnter command index to send (or 'q' to quit): ").strip().lower()
                    if cmd_choice == 'q':
                        break
                    
                    cmd_index = int(cmd_choice)
                    cmd_name = list(COMMANDS.keys())[cmd_index]
                    cmd_bytes = COMMANDS[cmd_name]
                    
                    print(f"--> Sending {cmd_name} ({cmd_bytes.hex(' ').upper()})")
                    ser.write(cmd_bytes)
                    
                    # Listen for a moment to see if there's any immediate response
                    time.sleep(0.2)
                    response = ser.read(100)
                    if response:
                        print(f"<-- Received response: {response.hex(' ').upper()}")
                    else:
                        print("<-- No immediate response received.")

                except (ValueError, IndexError):
                    print("Invalid command index.")
                except Exception as e:
                    print(f"An error occurred: {e}")

    except serial.SerialException as e:
        print(f"Error opening or using serial port {port}: {e}")
    except KeyboardInterrupt:
        print("\nExiting controller.")

if __name__ == "__main__":
    main()

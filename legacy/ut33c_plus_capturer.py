#!/usr/bin/env python3
"""UT33C+ Guided Capture Script
Guides the user through various multimeter modes/ranges and captures data.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Optional

try:
    import serial
except ImportError:
    print("Error: pyserial not found. Install with: pip install pyserial")
    sys.exit(1)

# Protocol Constants
BAUD = 2400
FRAME_LEN = 10
MARKER = bytes([0xAB, 0xCD])

def checksum_ok(frame: bytes) -> bool:
    if len(frame) != 10: return False
    # CS = (MODE + RANGE + B0 + B1 + B2 + B3 + B4) & 0xFF
    # Bytes: AB CD MODE RANGE B0 B1 B2 B3 B4 CS
    #        0  1  2    3     4  5  6  7  8  9
    expected = sum(frame[2:9]) & 0xFF
    return frame[9] == expected

def find_frames(buffer: bytearray) -> List[dict]:
    """Finds frames starting with AB CD marker. Returns dict with 'frame' and 'cs_ok'."""
    results = []
    i = 0
    while i <= len(buffer) - 10:
        # Search for marker AB CD
        if buffer[i] == 0xAB and buffer[i+1] == 0xCD:
            candidate = bytes(buffer[i:i+10])
            is_ok = checksum_ok(candidate)
            results.append({"frame": candidate, "cs_ok": is_ok})
            
            # Consume the frame and reset search
            del buffer[:i+10]
            i = 0
            continue
        i += 1
    
    # Safety: if buffer gets too long without finding markers, trim it
    if len(buffer) > 100:
        del buffer[:50]
        
    return results

def get_serial_port():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    if not ports:
        return None
    print("\nAvailable Serial Ports:")
    for i, p in enumerate(ports):
        print(f"[{i}] {p.device} ({p.description})")
    
    while True:
        try:
            choice = input("\nSelect port index: ").strip()
            if not choice: return ports[0].device
            idx = int(choice)
            if 0 <= idx < len(ports):
                return ports[idx].device
        except ValueError:
            pass
        print("Invalid selection.")

TEST_CASES = [
    {"name": "DCV 200mV", "instruction": "Set dial to 200m DCV. Connect a low voltage source (e.g. 100mV)."},
    {"name": "DCV 2V", "instruction": "Set dial to 2V DCV. Connect a 1.5V battery."},
    {"name": "DCV 20V", "instruction": "Set dial to 20V DCV. Connect a 9V or 12V source."},
    {"name": "DCV 200V", "instruction": "Set dial to 200V DCV. Connect a safe DC source >20V."},
    {"name": "DCV 600V", "instruction": "Set dial to 600V DCV. (Caution!)"},
    {"name": "ACV 200V", "instruction": "Set dial to 200V ACV."},
    {"name": "ACV 600V", "instruction": "Set dial to 600V ACV. (Caution!)"},
    {"name": "Resistance 200", "instruction": "Set dial to 200 Ohm. Connect a small resistor (e.g. 10 or 100 Ohm)."},
    {"name": "Resistance 2k", "instruction": "Set dial to 2k Ohm. Connect a 1k Ohm resistor."},
    {"name": "Resistance 20k", "instruction": "Set dial to 20k Ohm. Connect a 10k Ohm resistor."},
    {"name": "Resistance 200k", "instruction": "Set dial to 200k Ohm. Connect a 100k Ohm resistor."},
    {"name": "Resistance 20M", "instruction": "Set dial to 20M Ohm. Connect a 10M Ohm resistor."},
    {"name": "Resistance 200M", "instruction": "Set dial to 200M Ohm. (If available)."},
    {"name": "Continuity", "instruction": "Set dial to Continuity. Short the probes."},
    {"name": "Diode", "instruction": "Set dial to Diode. Connect a diode or short probes."},
    {"name": "DCA 200uA", "instruction": "Set dial to 200uA DC. Measure a small current."},
    {"name": "DCA 2mA", "instruction": "Set dial to 2mA DC."},
    {"name": "DCA 20mA", "instruction": "Set dial to 20mA DC."},
    {"name": "DCA 200mA", "instruction": "Set dial to 200mA DC."},
    {"name": "DCA 10A", "instruction": "Set dial to 10A DC. (Move red probe!)"},
    {"name": "Temperature C", "instruction": "Set dial to Temp C. Connect thermocouple."},
    {"name": "Temperature F", "instruction": "Set dial to Temp F. Connect thermocouple."},
    {"name": "OL State", "instruction": "Set to any low range and cause Overload (OL)."},
    {"name": "Hold Mode", "instruction": "Press HOLD button in any mode."},
    {"name": "Low Battery", "instruction": "Trigger low battery icon if possible."},
]

def run_test(ser: serial.Serial, test_case: dict) -> Optional[dict]:
    print("\n" + "="*40)
    print(f"TEST: {test_case['name']}")
    print(f"INSTRUCTION: {test_case['instruction']}")
    print("="*40)
    
    input("Press Enter when ready to start capturing (or Ctrl+C to skip/abort)...")
    
    print("Capturing data (looking for AB CD marker)...")
    captured_frames = []
    buffer = bytearray()
    start_time = time.time()
    last_raw_dump = time.time()
    timeout = 15
    
    while (time.time() - start_time) < timeout:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            buffer.extend(data)
            
            # Diagnostic: Print raw hex if we haven't found any frames yet
            if not captured_frames and (time.time() - last_raw_dump) > 2.0:
                raw_hex = data.hex(' ').upper()
                print(f"  [RAW DATA]: {raw_hex} ...")
                last_raw_dump = time.time()

            found_items = find_frames(buffer)
            for item in found_items:
                f = item['frame']
                cs_status = "[CS OK]" if item['cs_ok'] else "[CS ERR]"
                hex_f = f.hex(' ').upper()
                print(f"  Frame: {hex_f} {cs_status}")
                captured_frames.append(hex_f)
                
                # Stability check: last 4 frames are identical
                if len(captured_frames) >= 4:
                    last_four = captured_frames[-4:]
                    if len(set(last_four)) == 1:
                        print(f"\n[STABLE DATA DETECTED] {cs_status}")
                        print(f"Capture complete.")
                        display_val = input("What is the EXACT value displayed on the meter screen? (e.g. 10.01, 150.4, OL): ").strip()
                        
                        return {
                            "timestamp": datetime.now().isoformat(),
                            "test_name": test_case['name'],
                            "instruction": test_case['instruction'],
                            "displayed_value": display_val,
                            "frames": last_four,
                            "checksum_valid": item['cs_ok']
                        }
        time.sleep(0.05)
    
    if not captured_frames:
        print("\nError: No frames found with AB CD marker.")
        print(f"Last buffer state: {buffer.hex(' ').upper()}")
        return None
    
    print("\nTimeout reached without stability. Saving last captures.")
    display_val = input("What is the EXACT value displayed on the meter screen? (e.g. 10.01, 150.4, OL): ").strip()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "test_name": test_case['name'],
        "instruction": test_case['instruction'],
        "displayed_value": display_val,
        "frames": captured_frames[-5:],
        "checksum_valid": "mixed/unknown"
    }

def main():
    parser = argparse.ArgumentParser(description="UT33C+ Guided Capture")
    parser.add_argument("--port", help="Serial port")
    parser.add_argument("--out", default="captures.json", help="Output JSON file")
    args = parser.parse_args()

    port = args.port or get_serial_port()
    if not port:
        print("No serial port selected. Exiting.")
        return

    log_data = []
    if os.path.exists(args.out):
        try:
            with open(args.out, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except (OSError, json.JSONDecodeError):
            print(f"Warning: Could not load existing {args.out}. Starting fresh.")

    try:
        with serial.Serial(port, BAUD, timeout=0.1) as ser:
            print(f"Connected to {port} at {BAUD} baud.")
            
            while True:
                print("\nMain Menu:")
                for i, tc in enumerate(TEST_CASES):
                    status = " [DONE]" if any(d['test_name'] == tc['name'] for d in log_data) else ""
                    print(f"[{i:2}] {tc['name']}{status}")
                print("[q] Quit")
                
                choice = input("\nSelect test index to run (or 'q'): ").strip().lower()
                if choice == 'q':
                    break
                
                try:
                    idx = int(choice)
                    if 0 <= idx < len(TEST_CASES):
                        result = run_test(ser, TEST_CASES[idx])
                        if result:
                            log_data.append(result)
                            with open(args.out, "w", encoding="utf-8") as f:
                                json.dump(log_data, f, indent=2)
                            print(f"Saved to {args.out}")
                    else:
                        print("Invalid index.")
                except ValueError:
                    print("Invalid input.")
                except KeyboardInterrupt:
                    print("\nTest aborted.")
                    continue
                    
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nExiting.")

if __name__ == "__main__":
    main()

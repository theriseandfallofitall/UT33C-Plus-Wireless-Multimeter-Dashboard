import sys
import subprocess
import time
import re
from datetime import datetime

# Generate a wide range of commands to test
COMMANDS_TO_TEST = [
    # Bootloader Sync / Authorization prefixes
    "A5",
    "55",
    "AA",
    "06",
    "15",
    "81",
    "41",
    "A5 00",
    "A5 FF",
]

# Add A5 + all single bytes
for i in range(256):
    COMMANDS_TO_TEST.append(f"A5 {i:02X}")

# Add full valid frames for 20V (0D) and 200mV (17)
COMMANDS_TO_TEST.extend([
    "A5 AB CD 01 0D 00 00 00 00 1B",
    "AB CD 01 0D 00 00 00 00 1B",
    "AB CD 00 0D 00 00 00 00 1B", 
    "A5 AB CD 01 17 00 00 00 00 25",
    "AB CD 01 17 00 00 00 00 25",
])

BAUD_RATES = ["2400", "9600", "115200"]

def run_fuzzer():
    print(f"Starting Autonomous Multi-Baud Sweep at {datetime.now().isoformat()}")
    print("Assuming HOLD/SELECT is taped down.")
    
    for baud in BAUD_RATES:
        print(f"\n==============================")
        print(f"   TESTING BAUD RATE {baud}")
        print(f"==============================")
        
        subprocess.run(['python', '-m', 'tools.pico_rig_runner', 'cmd', f"UART INT {baud}"], capture_output=True)
        time.sleep(0.5)

        for cmd in COMMANDS_TO_TEST:
            rig_cmd = f"CYCLE_MARKER INT 2000 500 FD RESP {cmd}"
            
            result = subprocess.run(
                ['python', '-m', 'tools.pico_rig_runner', 'cmd', rig_cmd],
                capture_output=True,
                text=True
            )
            
            output = result.stdout
            
            # Switch back to 2400 to read the result!
            if baud != "2400":
                subprocess.run(['python', '-m', 'tools.pico_rig_runner', 'cmd', "UART INT 2400"], capture_output=True)
                time.sleep(0.1)
                # Then we monitor to see if it changed
                mon_result = subprocess.run(['python', '-m', 'tools.pico_rig_runner', 'cmd', "MONITOR INT 500"], capture_output=True, text=True)
                output += mon_result.stdout

            match = re.search(r'DATA INT.*?AB CD 01 ([0-9A-F]{2})', output, re.DOTALL)
            if match:
                mode_byte = match.group(1)
                if mode_byte != "19":
                    print(f">>> !!! MODE CHANGE DETECTED !!! <<<")
                    print(f"Payload [{cmd}] at {baud} baud caused mode change to {mode_byte}!")
                    # Keep it here
                    sys.exit(0)
                else:
                    # Print concisely to avoid log spam
                    print(f"Tested [{cmd}] at {baud} -> Mode {mode_byte} (No Change)")
            else:
                print(f"Tested [{cmd}] at {baud} -> No valid frame seen.")
                
            time.sleep(0.1) # Small gap between runs

if __name__ == '__main__':
    run_fuzzer()

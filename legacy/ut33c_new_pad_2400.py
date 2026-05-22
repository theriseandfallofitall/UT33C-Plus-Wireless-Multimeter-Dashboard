import serial
import time

port = "COM5"
baud_test = 2400
cmd_hex = "AB 06" # HOLD

def test_new_pad_2400(port):
    print(f"Testing NEW PAD (next to original TX) as a CONTROL port at {baud_test} baud...")
    print(f"Sending {cmd_hex}...")
    
    try:
        with serial.Serial(port, baud_test, timeout=0.5) as ser:
            cmd = bytes.fromhex(cmd_hex)
            ser.write(cmd)
            ser.flush()
            
            print("Watching for beeps or response...")
            time.sleep(1.0)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_new_pad_2400(port)

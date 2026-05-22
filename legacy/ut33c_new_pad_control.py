import serial
import time

port = "COM5"
baud_test = 4800
cmd_hex = "AB 06" # HOLD

def test_new_pad_bidirectional(port):
    print(f"Testing NEW PAD (next to original TX) as a CONTROL port at {baud_test} baud...")
    print(f"Sending {cmd_hex}...")
    
    try:
        with serial.Serial(port, baud_test, timeout=0.5) as ser:
            cmd = bytes.fromhex(cmd_hex)
            ser.write(cmd)
            ser.flush()
            
            print("Watching for response or beeps...")
            start = time.time()
            while time.time() - start < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"RECV: {data.hex(' ').upper()}")
                time.sleep(0.1)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("ACTION: Connect your FTDI TX wire to the NEW pad (next to the original TX).")
    input("Press Enter when connected...")
    test_new_pad_bidirectional(port)

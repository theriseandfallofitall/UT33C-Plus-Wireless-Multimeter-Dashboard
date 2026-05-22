import serial
import time

port = "COM5"

def trigger_and_poll():
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            print("Resetting...")
            ser.dtr = True
            ser.rts = True
            time.sleep(0.2)
            ser.dtr = False
            ser.rts = False
            time.sleep(0.5)
            
            print("Sending Wakeup/Poll bytes...")
            # Try a few common ones
            for b in [0x51, 0xAB, 0x05]:
                print(f"  Sending {hex(b)}")
                ser.write(bytes([b]))
                time.sleep(0.2)
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  !! RESPONSE: {data.hex(' ').upper()}")
                
            print("Final Monitoring...")
            start = time.time()
            while time.time() - start < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"RECV: {data.hex(' ').upper()}")
                time.sleep(0.1)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_and_poll()

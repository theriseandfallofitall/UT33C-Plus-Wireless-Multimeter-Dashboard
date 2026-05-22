import serial
import time
import sys

def monitor_and_send(port, baud=2400):
    print(f"Monitoring and sending SELECT command (AB 01) on {port}...")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            last_mode = None
            last_range = None
            
            # Send SELECT every 0.5s
            next_send = time.time()
            
            start_time = time.time()
            while time.time() - start_time < 10:
                if time.time() >= next_send:
                    ser.write(bytes.fromhex("AB 01"))
                    ser.flush()
                    next_send = time.time() + 0.5
                
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    # Simple frame detection
                    for i in range(len(data) - 9):
                        if data[i:i+2] == b'\xAB\xCD':
                            frame = data[i:i+10]
                            if len(frame) < 10: continue
                            mode = frame[2]
                            range_id = frame[3]
                            if last_mode is None or mode != last_mode or range_id != last_range:
                                print(f"[{time.strftime('%H:%M:%S')}] Frame: {frame.hex(' ').upper()} (Mode: {mode:02X}, Range: {range_id:02X})")
                                last_mode = mode
                                last_range = range_id
                time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_and_send("COM5")

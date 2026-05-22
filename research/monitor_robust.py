import serial
import time
import sys

def monitor_and_send_robust(port, baud=2400):
    print(f"Monitoring and sending SELECT command (AB 01) on {port}...")
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            last_mode = None
            last_range = None
            buffer = bytearray()
            
            # Send SELECT every 0.5s
            next_send = time.time()
            
            start_time = time.time()
            while time.time() - start_time < 15:
                if time.time() >= next_send:
                    ser.write(bytes.fromhex("AB 01"))
                    ser.flush()
                    print("  [SENT SELECT]")
                    next_send = time.time() + 1.0
                
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    buffer.extend(data)
                    
                    while len(buffer) >= 10:
                        idx = buffer.find(b'\xAB\xCD')
                        if idx == -1:
                            buffer.clear()
                            break
                        if idx > 0:
                            del buffer[:idx]
                            continue
                        
                        frame = bytes(buffer[:10])
                        mode = frame[2]
                        range_id = frame[3]
                        if last_mode is None or mode != last_mode or range_id != last_range:
                            print(f"[{time.strftime('%H:%M:%S')}] RECV: {frame.hex(' ').upper()} (Mode: {mode:02X}, Range: {range_id:02X})")
                            last_mode = mode
                            last_range = range_id
                        del buffer[:10]
                time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_and_send_robust("COM5")

import time
import serial

def wdt_crash():
    print("Testing Watchdog crash via NULL stream during boot window...")
    
    # 1. Connect to Rig
    ser = serial.Serial('COM6', 115200, timeout=1)
    
    # 2. Hard power off
    ser.write(b"POWER OFF\n")
    time.sleep(5)
    
    # 3. Read everything
    ser.read_all()
    
    # 4. Turn on and immediately stream NULLs
    ser.write(b"POWER ON\n")
    
    start = time.time()
    while time.time() - start < 5.0:
        # We need to send NULLs out the Pico's INT port.
        # But we can only do this via TX commands, which are too slow.
        # We can do NULLS INT 200 0 to send 200 nulls instantly.
        ser.write(b"NULLS INT 200 0\n")
        time.sleep(0.01)
        
    print("Crash stream sent. Checking status...")
    
    # Wait for things to settle
    time.sleep(2)
    ser.read_all()
    
    ser.write(b"MONITOR INT 2000\n")
    time.sleep(2.5)
    output = ser.read_all().decode(errors='replace')
    
    if "19 00 00" in output:
        print("MCU recovered to normal measurement (Mode 19).")
    elif "41" in output or "81" in output:
        print("!!! MCU IN DIAGNOSTIC STATE !!!")
    else:
        print("No normal output seen. It might be hung.")
    
    print("Output:\\n", output)

if __name__ == '__main__':
    wdt_crash()

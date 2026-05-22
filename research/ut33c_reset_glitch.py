import serial
import time

port = "COM5"

def high_freq_reset_glitch(iterations=100, delay=0.01):
    print(f"Starting high-frequency reset pulsing on {port}...")
    print(f"Pulsing {iterations} times with {delay}s delay...")
    
    try:
        with serial.Serial(port, 2400, timeout=0.1) as ser:
            for i in range(iterations):
                # Pulse Reset Low (assuming RTS/DTR pulls RST pad to GND)
                ser.dtr = True
                ser.rts = True
                time.sleep(delay)
                
                # Release Reset
                ser.dtr = False
                ser.rts = False
                time.sleep(delay)
                
                if i % 20 == 0:
                    print(f"  Pulse {i}...")
                
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  [DATA AT PULSE {i}]: {data.hex(' ').upper()}")
            
            print("\nPulsing complete. Monitoring for 5 seconds for any new state...")
            start = time.time()
            while time.time() - start < 5:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"  RECV: {data.hex(' ').upper()}")
                time.sleep(0.01)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Try very fast 10ms pulses
    high_freq_reset_glitch(iterations=200, delay=0.01)

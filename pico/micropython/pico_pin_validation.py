from machine import Pin, UART
import time

# --- Pin Definitions (Matching PICO_WIRING.md) ---
pwr_fet = Pin(16, Pin.OUT, value=1) # Power FET
pad1 = Pin(14, Pin.OUT, value=0)    # Soft Reset (Pad 1)
pad2 = Pin(15, Pin.OUT, value=0)    # Hard Reset (Pad 2)

# UART0: Internal Pads (GP0=TX, GP1=RX)
uart0 = UART(0, baudrate=2400, tx=Pin(0), rx=Pin(1), timeout=100)
# UART1: External Pads (GP4=TX, GP5=RX)
uart1 = UART(1, baudrate=2400, tx=Pin(4), rx=Pin(5), timeout=100)

def test_hardware():
    print("--- Pi Pico Pin Validation Script ---")
    
    # 1. Test Power Control
    print("\n1. Testing Power Control (GP16)...")
    print("   Meter should turn OFF now (3 seconds)...")
    pwr_fet.value(0)
    time.sleep(3)
    print("   Meter should turn ON now...")
    pwr_fet.value(1)
    time.sleep(2)
    
    # 2. Test Soft Reset
    print("\n2. Testing Soft Reset (GP14 / Pad 1)...")
    print("   Meter should give a LONG BEEP now...")
    pad1.value(1)
    time.sleep(0.3)
    pad1.value(0)
    time.sleep(2)
    
    # 3. Test Hard Reset
    print("\n3. Testing Hard Reset (GP15 / Pad 2)...")
    print("   Meter screen should BLANK and REBOOT now...")
    pad2.value(1)
    time.sleep(0.3)
    pad2.value(0)
    time.sleep(2)
    
    # 4. Test UART Data Flow
    print("\n4. Testing UART Data Flow (10 second monitor)...")
    print("   Waiting for data from BOTH ports at 2400 baud...")
    
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < 10000:
        if uart0.any():
            data = uart0.read()
            print("[INTERNAL GP1] RECV: {}".format(data.hex().upper()))
            
        if uart1.any():
            data = uart1.read()
            print("[EXTERNAL GP5] RECV: {}".format(data.hex().upper()))
            
        time.sleep_ms(10)

    print("\n--- Validation Sequence Complete ---")

if __name__ == "__main__":
    test_hardware()

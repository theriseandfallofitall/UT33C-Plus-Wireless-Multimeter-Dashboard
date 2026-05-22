from machine import Pin, UART
import time

# --- Success Detection Configuration ---
# We are looking for any Mode Byte (Byte 3) that is NOT the default 0x17 (200mV)
DEFAULT_RANGE = 0x17 

# --- Hardware Configuration (RP2350) ---
uart_int = UART(0, baudrate=2400, tx=Pin(0), rx=Pin(1))
uart_ext = UART(1, baudrate=2400, tx=Pin(4), rx=Pin(5))

pad1 = Pin(14, Pin.OUT, value=0)
pad2 = Pin(15, Pin.OUT, value=0)
pwr_fet = Pin(16, Pin.OUT, value=1)

def log(msg, success=False):
    prefix = "!!! SUCCESS !!! " if success else ""
    print("[{}] {}{}".format(time.ticks_ms(), prefix, msg))

def check_for_success(data, port_name):
    """Analyzes 10-byte frames for changes in state."""
    if len(data) >= 10:
        for i in range(len(data) - 9):
            if data[i] == 0xAB and data[i+1] == 0xCD:
                mode_byte = data[i+3]
                if mode_byte != DEFAULT_RANGE:
                    log("MODE CHANGE DETECTED on {}: New Mode 0x{:02X}".format(port_name, mode_byte), True)
                    return True
    return False

def fuzz_cycle():
    log("=== STARTING AUTONOMOUS SEARCH ===")
    cycle_count = 0
    
    while True:
        cycle_count += 1
        log("Cycle #{} | Power Cycling...".format(cycle_count))
        
        # 1. Power Off
        pwr_fet.value(0)
        time.sleep_ms(800)
        
        # 2. Power On
        pwr_fet.value(1)
        
        # 3. Injection Window (The first 2 seconds of boot)
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < 3000:
            # Blast SELECT (AB 01)
            uart_int.write(b'\xAB\x01')
            uart_ext.write(b'\xAB\x01')
            
            # Check for responses
            if uart_int.any():
                raw = uart_int.read()
                if check_for_success(raw, "INTERNAL"):
                    # If we win, keep the power on so we can see the screen!
                    log("SUCCESS ACHIEVED. PAUSING FUZZER.")
                    while True: time.sleep(1)
                
            if uart_ext.any():
                raw = uart_ext.read()
                check_for_success(raw, "EXTERNAL")
                
            time.sleep_ms(50) # Injection frequency
            
        log("Cycle complete. No breakthrough. Retrying...")
        time.sleep_ms(500)

if __name__ == "__main__":
    fuzz_cycle()

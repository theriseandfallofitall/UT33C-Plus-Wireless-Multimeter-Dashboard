from machine import Pin, UART
import time
import uos

# --- Hardware Configuration ---
# UART0: Internal Pads (GP0=TX, GP1=RX)
uart_int = UART(0, baudrate=2400, tx=Pin(0), rx=Pin(1), timeout=100)
# UART1: External Pads (GP4=TX, GP5=RX)
uart_ext = UART(1, baudrate=2400, tx=Pin(4), rx=Pin(5), timeout=100)

pad1 = Pin(14, Pin.OUT, value=0) # Soft Reset
pad2 = Pin(15, Pin.OUT, value=0) # Hard Reset
pwr_fet = Pin(16, Pin.OUT, value=1) # Power FET (1=ON, 0=OFF)

def log(msg):
    print("[{}] {}".format(time.ticks_ms(), msg))

def power_cycle(duration=0.5):
    log("Powering OFF...")
    pwr_fet.value(0)
    time.sleep(1.0)
    log("Powering ON...")
    pwr_fet.value(1)
    time.sleep(duration)

def pulse_reset(pin, duration_ms=200):
    log("Pulsing Reset on Pin {}...".format(pin))
    pin.value(1)
    time.sleep_ms(duration_ms)
    pin.value(0)

def monitor_all(duration_s=2):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < (duration_s * 1000):
        # Check Internal Port
        if uart_int.any():
            data = uart_int.read()
            log("INT RECV: {}".format(data.hex().upper()))
        
        # Check External Port
        if uart_ext.any():
            data = uart_ext.read()
            log("EXT RECV: {}".format(data.hex().upper()))
        
        time.sleep_ms(10)

def fuzz_loop():
    log("=== STARTING PICO AUTO-FUZZER ===")
    
    # Sequence 1: Baud rate discovery on boot
    bauds = [2400, 4800, 9600]
    for b in bauds:
        log("\n--- Testing Boot at {} baud ---".format(b))
        uart_int.init(baudrate=b)
        uart_ext.init(baudrate=b)
        power_cycle(0.2) # Power on and immediately listen
        monitor_all(3)

    # Sequence 2: Injection during Hard Reset
    log("\n--- Starting Injection Fuzzing (Pad 2) ---")
    uart_int.init(baudrate=2400)
    uart_ext.init(baudrate=2400)
    
    injections = [b'\xAB\x00', b'\xAB\x01', b'\x55\xAA', b'\x7F']
    for cmd in injections:
        log("Injecting: {}".format(cmd.hex().upper()))
        pulse_reset(pad2, 100)
        # Blast during release
        for _ in range(20):
            uart_int.write(cmd)
            uart_ext.write(cmd)
        monitor_all(2)

    log("\n=== FUZZING COMPLETE ===")

if __name__ == "__main__":
    fuzz_loop()

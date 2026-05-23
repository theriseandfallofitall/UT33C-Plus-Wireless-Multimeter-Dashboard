#!/usr/bin/env python3
"""
UT33C+ Automated Hardware Test Rig
----------------------------------
This script is designed to run on a custom hardware rig that can control:
1. Internal UART Pads (TX/RX)
2. External Opto UART Pads (TX/RX)
3. Pad 1 (Soft Reset)
4. Pad 2 (Hard Reset)
5. Power Supply (Power Cycler)

Configure the ports and pin mappings in the RIG_CONFIG dictionary below.
"""

import serial
import time
import os
import threading
import sys
from datetime import datetime

# ==========================================
# HARDWARE RIG CONFIGURATION
# Modify these to match your actual wiring
# ==========================================
RIG_CONFIG = {
    # Serial port connected to the "New" internal pads
    "PORT_INTERNAL": "COM5",
    
    # Serial port connected to the "Old" external opto pads
    "PORT_EXTERNAL": "COM6",
    
    # Define how the physical pins are controlled.
    # Example: "internal_dtr" means the DTR pin on the PORT_INTERNAL serial adapter.
    "PAD1_PIN": "internal_dtr",  
    "PAD2_PIN": "internal_rts",
    "POWER_PIN": "external_dtr", # e.g., controls a relay for VCC
    
    # Logic levels for activation
    "POWER_ACTIVE_HIGH": True,
    "PAD_ACTIVE_HIGH": True, # Set to True if your rig inverts the signal to pull to GND
}

class TestRig:
    def __init__(self, config):
        self.cfg = config
        self.ser_int = None
        self.ser_ext = None
        self.log_file = None
        self.setup_ports()

    def setup_ports(self):
        print("Initializing Hardware Rig...")
        try:
            # Open ports at a default baud rate just to hold the hardware lines
            self.ser_int = serial.Serial(self.cfg["PORT_INTERNAL"], 2400, timeout=0.1)
            self.ser_ext = serial.Serial(self.cfg["PORT_EXTERNAL"], 2400, timeout=0.1)
            
            # Ensure everything is in a safe/off state
            self._set_pin(self.cfg["PAD1_PIN"], False)
            self._set_pin(self.cfg["PAD2_PIN"], False)
            self.power_on() # Start with power on
            print("Hardware initialized successfully.")
        except Exception as e:
            print(f"FAILED to initialize ports. Check your COM port numbers. Error: {e}")
            sys.exit(1)

    def _set_pin(self, pin_name, state):
        """Helper to route abstract pin names to actual FTDI hardware lines."""
        if pin_name == "internal_dtr": self.ser_int.dtr = state
        elif pin_name == "internal_rts": self.ser_int.rts = state
        elif pin_name == "external_dtr": self.ser_ext.dtr = state
        elif pin_name == "external_rts": self.ser_ext.rts = state

    # --- Hardware Control Methods ---

    def power_off(self):
        print("  [RIG] Powering OFF...")
        self._set_pin(self.cfg["POWER_PIN"], not self.cfg["POWER_ACTIVE_HIGH"])
        time.sleep(1) # Let caps discharge

    def power_on(self):
        print("  [RIG] Powering ON...")
        self._set_pin(self.cfg["POWER_PIN"], self.cfg["POWER_ACTIVE_HIGH"])
        time.sleep(0.5)

    def power_cycle(self):
        self.power_off()
        self.power_on()

    def pulse_pad1(self, duration=0.2):
        print("  [RIG] Pulsing Pad 1 (Soft Reset)...")
        self._set_pin(self.cfg["PAD1_PIN"], self.cfg["PAD_ACTIVE_HIGH"])
        time.sleep(duration)
        self._set_pin(self.cfg["PAD1_PIN"], not self.cfg["PAD_ACTIVE_HIGH"])

    def pulse_pad2(self, duration=0.2):
        print("  [RIG] Pulsing Pad 2 (Hard Reset)...")
        self._set_pin(self.cfg["PAD2_PIN"], self.cfg["PAD_ACTIVE_HIGH"])
        time.sleep(duration)
        self._set_pin(self.cfg["PAD2_PIN"], not self.cfg["PAD_ACTIVE_HIGH"])

    # --- Data Capture Methods ---

    def _capture_worker(self, ser, port_name, duration, results):
        """Thread worker to capture data from a serial port."""
        start = time.time()
        buffer = bytearray()
        while time.time() - start < duration:
            if ser.in_waiting:
                buffer.extend(ser.read(ser.in_waiting))
            time.sleep(0.01)
        results[port_name] = buffer

    def capture_both(self, duration=5.0):
        """Captures data from both ports simultaneously."""
        results = {}
        t_int = threading.Thread(target=self._capture_worker, args=(self.ser_int, "INTERNAL", duration, results))
        t_ext = threading.Thread(target=self._capture_worker, args=(self.ser_ext, "EXTERNAL", duration, results))
        
        t_int.start()
        t_ext.start()
        t_int.join()
        t_ext.join()
        
        return results

    def set_baud(self, baud):
        self.ser_int.baudrate = baud
        self.ser_ext.baudrate = baud

    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        out = f"[{ts}] {message}"
        print(out)
        if self.log_file:
            self.log_file.write(out + "\n")

    def shutdown(self):
        self.power_off()
        if self.ser_int: self.ser_int.close()
        if self.ser_ext: self.ser_ext.close()
        if self.log_file: self.log_file.close()

# ==========================================
# AUTOMATED TEST SEQUENCES
# ==========================================

def run_automated_suite(config):
    rig = TestRig(config)
    
    # Setup logging
    if not os.path.exists("logs"): os.makedirs("logs")
    filename = f"logs/automated_fuzz_{int(time.time())}.txt"
    rig.log_file = open(filename, "w")
    rig.log(f"Starting Automated Test Suite. Logging to {filename}")

    try:
        # ---------------------------------------------------------
        # PHASE 1: Power Cycle Boot Monitoring at various bauds
        # ---------------------------------------------------------
        rig.log("\n=== PHASE 1: Boot Sequence Monitoring ===")
        bauds_to_test = [2400, 4800, 9600, 115200]
        
        for baud in bauds_to_test:
            rig.log(f"\n--- Testing Boot at {baud} baud ---")
            rig.set_baud(baud)
            rig.power_off()
            
            # Start listening just before power on
            capture_thread = threading.Thread(target=lambda: capture_results.update(rig.capture_both(duration=4.0)))
            capture_results = {}
            capture_thread.start()
            
            time.sleep(0.5)
            rig.power_on()
            capture_thread.join()
            
            for port, data in capture_results.items():
                if data:
                    rig.log(f"  {port} RECV: {data.hex(' ').upper()}")
                else:
                    rig.log(f"  {port} RECV: (No Data)")

        # ---------------------------------------------------------
        # PHASE 2: Pad 2 (Hard Reset) Fuzzing
        # ---------------------------------------------------------
        rig.log("\n=== PHASE 2: Hard Reset (Pad 2) Fuzzing ===")
        rig.set_baud(2400) # Reset to default
        
        fuzz_chars = [b'', b'\x55', b'\xAA', b'\xAB\x01', b'\x00']
        
        for char in fuzz_chars:
            char_desc = "None (Listen only)" if not char else char.hex(' ').upper()
            rig.log(f"\n--- Fuzzing Pad 2 with Injection: {char_desc} ---")
            
            # Pulse Reset
            rig.pulse_pad2()
            
            # Inject on both ports
            if char:
                rig.ser_int.write(char)
                rig.ser_ext.write(char)
            
            # Listen for results
            res = rig.capture_both(duration=3.0)
            for port, data in res.items():
                if data:
                    # Filter out standard AB CD if it's overwhelming, or just log snippet
                    snippet = data[:20].hex(' ').upper() + ("..." if len(data)>20 else "")
                    rig.log(f"  {port} RESP: {snippet}")

        # ---------------------------------------------------------
        # PHASE 3: Baud Rate Sweep with Continuous Polling
        # ---------------------------------------------------------
        rig.log("\n=== PHASE 3: Continuous Poll Sweep ===")
        poll_cmd = bytes.fromhex("AB 00")
        
        for baud in [2400, 4800, 9600]:
            rig.log(f"\n--- Sweeping {baud} baud ---")
            rig.set_baud(baud)
            
            # Send 5 polls
            for _ in range(5):
                rig.ser_int.write(poll_cmd)
                rig.ser_ext.write(poll_cmd)
                time.sleep(0.1)
                
            res = rig.capture_both(duration=2.0)
            for port, data in res.items():
                if data: rig.log(f"  {port} RESP: {data[:20].hex(' ').upper()}")

        rig.log("\n=== AUTOMATED SUITE COMPLETE ===")

    except KeyboardInterrupt:
        rig.log("\nSuite aborted by user.")
    except Exception as e:
        rig.log(f"\nCritical Error during suite: {e}")
    finally:
        rig.shutdown()
        print("Rig powered down safely.")

if __name__ == "__main__":
    run_automated_suite(RIG_CONFIG)

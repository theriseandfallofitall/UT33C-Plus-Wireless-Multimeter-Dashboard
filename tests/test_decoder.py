#!/usr/bin/env python3
import unittest
import os
import re
import sys
from pathlib import Path

# Add project root to path to allow importing the shared decoder.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ut33c.decoder import decode_reading, checksum_ok

class TestDecoder(unittest.TestCase):

    def load_fixture(self, log_name):
        """Loads the RAW_HEX data from a log file in the logs/ directory."""
        log_path = project_root / "logs" / log_name
        if not log_path.exists():
            raise FileNotFoundError(f"Fixture {log_name} not found in logs/")
        
        content = log_path.read_text()
        match = re.search(r"RAW_HEX:\s*([0-9A-Fa-f\s]+)", content)
        if not match:
            raise ValueError(f"Could not find RAW_HEX in {log_name}")
            
        hex_string = match.group(1).strip()
        byte_values = [int(b, 16) for b in hex_string.split()]
        
        # Find the first valid frame
        buffer = bytearray(byte_values)
        idx = buffer.find(b'\xAB\xCD')
        if idx == -1 or len(buffer) < idx + 10:
            raise ValueError(f"No valid frame header found in {log_name}")
            
        frame = bytes(buffer[idx:idx+10])
        return frame

    def test_checksum_validity(self):
        """Verify that our fixtures have valid checksums."""
        frame = self.load_fixture("10A_dc_mode__at_3.01A.log")
        self.assertTrue(checksum_ok(frame))
        
        # Tamper with a byte to invalidate checksum
        bad_frame = bytearray(frame)
        bad_frame[5] += 1
        self.assertFalse(checksum_ok(bytes(bad_frame)))

    def test_voltage_and_current(self):
        frame = self.load_fixture("10A_dc_mode__at_3.01A.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "10A DC")
        self.assertEqual(val, "3.01")
        self.assertEqual(unit, "A")

        frame = self.load_fixture("20m_range_1,21ma.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "20mA DC")
        self.assertEqual(val, "1.21")
        self.assertEqual(unit, "mA")

    def test_resistance_scaling(self):
        # 20k Range, 0.01 scale
        frame = self.load_fixture("20k_ohm_range_1,00k_ohm_resistor.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "20k Ohm")
        self.assertEqual(val, "1.00")
        self.assertEqual(unit, "kOhm")

        # 200k Range, 0.1 scale
        frame = self.load_fixture("143.7k_ohm_in_200k_mode.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "200k Ohm")
        self.assertEqual(val, "143.7")
        self.assertEqual(unit, "kOhm")

        # 2M Range, 0.01 scale (was 0.001)
        frame = self.load_fixture("1,05_Meg_ohm_in_200m_mode.log")
        # Note: log name is misleading, it's 2M mode. Real value is 1.05M
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "2M Ohm")
        # Raw value is 105, correct scale is 0.01 -> 1.05
        self.assertEqual(val, "1.05")
        self.assertEqual(unit, "MOhm")

    def test_temperature_conversion(self):
        # Celsius - straightforward scaling
        frame = self.load_fixture("celsius_mode_18_deg_c.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "Celsius")
        self.assertTrue(val in ["17.9", "18.2"]) # Log has fluctuations
        self.assertEqual(unit, "deg C")

        # Fahrenheit - requires C->F conversion
        frame = self.load_fixture("fahrenheit_measurement_at_64_f.log")
        # Raw value is ~175-182, which is ~17.5-18.2 C.
        # 17.8 * 9/5 + 32 = 64.04 F
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "Fahrenheit")
        self.assertAlmostEqual(float(val), 64.0, delta=1.0)
        self.assertEqual(unit, "deg F")

    def test_special_states_continuity_diode(self):
        # Diode voltage drop
        frame = self.load_fixture("diode_mode_0,608_diode_reading.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "Continuity")
        self.assertEqual(val, "0.608")
        self.assertEqual(unit, "V")

        # Continuity Open Loop (OL)
        frame = self.load_fixture("continuity_1779430312.log")
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "Continuity")
        self.assertEqual(val, "OL")
        self.assertEqual(unit, "Ohm")
        
    def test_200mv_offset(self):
        frame = self.load_fixture("power_on_to_200mv_setting_with_nothing_connected.log")
        # Raw value is 0, offset was -2000, now should be 0.
        mode, val, unit, _ = decode_reading(frame)
        self.assertEqual(mode, "200mV DC")
        self.assertEqual(val, "0.0")
        self.assertEqual(unit, "mV")

if __name__ == '__main__':
    unittest.main()

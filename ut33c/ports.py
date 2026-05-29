"""Serial-port discovery helpers for UT33C+ applications."""

from __future__ import annotations
import serial.tools.list_ports

# Keywords to look for in COM port descriptions
DISPLAY_PORT_KEYWORDS = (
    "UT33C",    # Custom Bluetooth Name
    "USB", 
    "FT232", 
    "PICO", 
    "RP2040", 
    "SERIAL", 
    "CH340", 
    "CP210"
)

def find_display_port() -> str | None:
    """Auto-detect the multimeter COM port based on keywords."""
    for port in serial.tools.list_ports.comports():
        text = f"{port.description} {port.hwid}".upper()
        if any(keyword in text for keyword in DISPLAY_PORT_KEYWORDS):
            return port.device
    return None

def list_all_ports() -> list[str]:
    """Returns a list of strings like 'COM8 - UT33C_MultiMeter'"""
    return [f"{port.device} - {port.description}" for port in serial.tools.list_ports.comports()]

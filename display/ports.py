"""Serial-port discovery helpers for display applications."""

from __future__ import annotations

import serial.tools.list_ports


DISPLAY_PORT_KEYWORDS = ("USB", "FT232", "PICO", "RP2040", "SERIAL", "CH340", "CP210")


def find_display_port() -> str | None:
    for port in serial.tools.list_ports.comports():
        text = f"{port.description} {port.hwid}".upper()
        if any(keyword in text for keyword in DISPLAY_PORT_KEYWORDS):
            return port.device
    return None

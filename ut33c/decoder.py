#!/usr/bin/env python3
"""
Shared UT33C+ UART protocol decoder.

The meter emits 10-byte binary frames at 2400 baud:
AB CD ID MODE B0 B1 B2 B3 STATUS CS
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BAUD = 2400
FRAME_HEADER = b"\xAB\xCD"
FRAME_SIZE = 10


@dataclass(frozen=True)
class Reading:
    mode: str
    value: str
    unit: str
    raw_value: int
    raw_hex: str


MODES: dict[int, dict[str, Any]] = {
    0x07: {"name": "2000mV DC", "unit": "mV", "scale": 1.0, "offset": 0},
    0x0B: {"name": "10A DC", "unit": "A", "scale": 0.01, "offset": 0},
    0x0D: {"name": "20V DC", "unit": "V", "scale": 0.01, "offset": 0},
    0x0E: {"name": "20k Ohm", "unit": "kOhm", "scale": 0.01, "offset": 0},
    0x0F: {"name": "200mA DC", "unit": "mA", "scale": 0.1, "offset": 0},
    0x11: {"name": "600V AC", "unit": "V", "scale": 1.0, "offset": 0},
    0x12: {"name": "200V AC", "unit": "V", "scale": 0.1, "offset": 0},
    0x13: {
        "name": "Fahrenheit",
        "unit": "deg F",
        "scale": 1.0,
        "offset": 0,
        "transform": "celsius_to_fahrenheit",
    },
    0x15: {"name": "200V DC", "unit": "V", "scale": 0.1, "offset": 0},
    0x16: {"name": "Celsius", "unit": "deg C", "scale": 0.1, "offset": 0},
    0x17: {"name": "200mV DC", "unit": "mV", "scale": 0.1, "offset": 0},
    0x18: {"name": "600V DC", "unit": "V", "scale": 1.0, "offset": 0},
    0x19: {
        "name": "Continuity",
        "unit": "Ohm",
        "scale": 1.0,
        "offset": 0,
        "transform": "continuity_diode",
    },
    0x1A: {"name": "200k Ohm", "unit": "kOhm", "scale": 0.1, "offset": 0},
    0x1B: {"name": "20mA DC", "unit": "mA", "scale": 0.01, "offset": 0},
    0x1C: {"name": "2M Ohm", "unit": "MOhm", "scale": 0.01, "offset": 0},
    0x1E: {"name": "2000 Ohm", "unit": "Ohm", "scale": 1.0, "offset": 0},
    0x1F: {"name": "2000uA DC", "unit": "uA", "scale": 1.0, "offset": 0},
}


def celsius_to_fahrenheit(celsius_val: float) -> float:
    return (celsius_val * 9 / 5) + 32


def continuity_diode(raw_val: int) -> tuple[str, str]:
    if raw_val >= 0x7F00:
        return "OL", "Ohm"
    if raw_val < 3000:
        return f"{raw_val / 1000.0:.3f}", "V"
    return f"{raw_val}", "Ohm"


def checksum_ok(frame: bytes) -> bool:
    if len(frame) != FRAME_SIZE:
        return False
    return sum(frame[2:8]) & 0xFF == frame[9]


def format_scaled_value(value: float, scale: float) -> str:
    if scale == 0.1:
        return f"{value:.1f}"
    if scale == 0.01:
        return f"{value:.2f}"
    if scale == 0.001:
        return f"{value:.3f}"
    return f"{int(value)}"


def decode_frame(frame: bytes) -> Reading:
    mode_byte = frame[3] & 0x7F
    raw_val = int.from_bytes(frame[4:8], byteorder="big", signed=True)
    raw_hex = frame.hex(" ").upper()

    if mode_byte not in MODES:
        return Reading(f"Unknown ({hex(mode_byte)})", "???", "raw", raw_val, raw_hex)

    mode = MODES[mode_byte]
    name = mode["name"]
    unit = mode["unit"]

    if raw_val >= 32767 or (mode_byte == 0x17 and raw_val >= 2080):
        return Reading(name, "OL", unit, raw_val, raw_hex)

    if "Ohm" in name and raw_val >= 0x7F00:
        return Reading(name, "OL", unit, raw_val, raw_hex)

    transform = mode.get("transform")
    if transform == "celsius_to_fahrenheit":
        value = celsius_to_fahrenheit(raw_val * 0.1)
        return Reading(name, f"{value:.1f}", unit, raw_val, raw_hex)

    if transform == "continuity_diode":
        value, transformed_unit = continuity_diode(raw_val)
        return Reading(name, value, transformed_unit, raw_val, raw_hex)

    value = (raw_val + mode.get("offset", 0)) * mode.get("scale", 1.0)
    return Reading(name, format_scaled_value(value, mode.get("scale", 1.0)), unit, raw_val, raw_hex)


def decode_reading(frame: bytes) -> tuple[str, str, str, int]:
    reading = decode_frame(frame)
    return reading.mode, reading.value, reading.unit, reading.raw_value


def pop_next_frame(buffer: bytearray) -> bytes | None:
    while len(buffer) >= FRAME_SIZE:
        idx = buffer.find(FRAME_HEADER)

        if idx == -1:
            if buffer[-1:] == FRAME_HEADER[:1]:
                del buffer[:-1]
            else:
                buffer.clear()
            return None

        if idx > 0:
            del buffer[:idx]
            continue

        frame = bytes(buffer[:FRAME_SIZE])
        if checksum_ok(frame):
            del buffer[:FRAME_SIZE]
            return frame

        del buffer[:1]

    return None

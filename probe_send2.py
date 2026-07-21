#!/usr/bin/env python3
"""Probe v2: distinguish a real meter reaction from a Bluetooth-link stall.
Baseline -> send payload -> watch recovery per-second for 10s.
Run twice: once with the real command, once with a random control payload.
Usage: probe_send2.py <port> [cmd|ctrl]"""

import sys, time, serial
from ut33c.decoder import BAUD, pop_next_frame, decode_frame

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/rfcomm0"
WHICH = sys.argv[2] if len(sys.argv) > 2 else "cmd"

CMD = bytes([0x06, 0xAB, 0xCD, 0x03, 0x5E, 0x01, 0xD9])
CTRL = bytes([0x55, 0x12, 0xF0, 0x9A, 0x37, 0x80, 0x44])  # same length, junk
PAYLOAD = CMD if WHICH == "cmd" else CTRL


def count_window(ser, seconds):
    buf, frames = bytearray(), 0
    end = time.time() + seconds
    while time.time() < end:
        if ser.in_waiting:
            buf.extend(ser.read(ser.in_waiting))
            while pop_next_frame(buf) is not None:
                frames += 1
        time.sleep(0.01)
    return frames


def main():
    print(f"Port {PORT} @ {BAUD} | payload={WHICH} {PAYLOAD.hex(' ').upper()}")
    with serial.Serial(PORT, BAUD, timeout=0.1) as ser:
        # warm up so we start from a healthy link, no buffer reset trickery
        base = count_window(ser, 3)
        print(f"baseline 3s: {base} frames ({base/3:.0f}/s)")
        ser.write(PAYLOAD); ser.flush()
        print(f"--> sent, watching recovery:")
        for i in range(10):
            n = count_window(ser, 1)
            print(f"  +{i+1}s: {n} frames")


if __name__ == "__main__":
    main()

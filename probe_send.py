#!/usr/bin/env python3
"""One-off probe: baseline-read, send a candidate command, read again, diff.
Bytes default to the UT61E+ query from mwuertinger/ut61ep (likely no effect on
the SD7501-based UT33C+, whose RX pad is unwired per docs/WIRING.md)."""

import sys, time, serial
from ut33c.decoder import BAUD, pop_next_frame, decode_frame

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/rfcomm0"
CMD = bytes([0x06, 0xAB, 0xCD, 0x03, 0x5E, 0x01, 0xD9])
WINDOW = 3.0  # seconds per capture phase


def capture(ser, label, seconds):
    buf, frames, raw = bytearray(), [], bytearray()
    end = time.time() + seconds
    while time.time() < end:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting)
            buf.extend(chunk); raw.extend(chunk)
            while (f := pop_next_frame(buf)) is not None:
                frames.append(decode_frame(f))
        time.sleep(0.01)
    print(f"[{label}] {len(raw)} bytes, {len(frames)} valid frames")
    if frames:
        r = frames[-1]
        print(f"  last: {r.mode} {r.value} {r.unit}")
    return bytes(raw)


def main():
    print(f"Port {PORT} @ {BAUD} 8N1")
    with serial.Serial(PORT, BAUD, timeout=0.1) as ser:
        before = capture(ser, "before", WINDOW)
        print(f"--> sending {CMD.hex(' ').upper()}")
        ser.reset_input_buffer()
        ser.write(CMD); ser.flush()
        after = capture(ser, "after", WINDOW)
    # look for anything that isn't a normal AB CD ... frame
    print("decision: stream unchanged" if before and after else "decision: check wiring/port")


if __name__ == "__main__":
    main()

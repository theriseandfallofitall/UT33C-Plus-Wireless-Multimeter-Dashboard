#!/usr/bin/env python3
"""Short raw USB serial sniff for Pico passthrough or rig output."""

import argparse
import time

import serial


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture raw bytes from Pico USB serial.")
    parser.add_argument("--port", default="COM6")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--seconds", type=float, default=5.0)
    args = parser.parse_args()

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as ser:
            print(f"Listening on {args.port} at {args.baud} baud for {args.seconds:g} seconds...")
            start = time.time()
            while time.time() - start < args.seconds:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    print(f"Data: {data.hex(' ')}")
                time.sleep(0.01)
            print("Done.")
    except serial.SerialException as exc:
        print(f"Serial error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

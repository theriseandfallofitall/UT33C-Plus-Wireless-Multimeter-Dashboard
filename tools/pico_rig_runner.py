#!/usr/bin/env python3
"""
Host-side controller for the UT33C+ Pico rig firmware.

Flash pico/cpp once, then run experiments from this script without rebuilding
or reflashing the Pico for each test.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import serial
import serial.tools.list_ports


BAUD = 115200
DEFAULT_PORT = "COM6"
LOG_DIR = Path("logs") / "rig_runs"
TERMINAL_PREFIXES = ("OK ", "ERR ")


def find_pico_port() -> str:
    for port in serial.tools.list_ports.comports():
        text = f"{port.description} {port.hwid}"
        if "2E8A" in text or "Pico" in text or "RP2040" in text or "USB Serial" in text:
            return port.device
    return DEFAULT_PORT


def now_label() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def line_ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


@dataclass
class RigLine:
    timestamp: str
    text: str


class SessionLog:
    def __init__(self, path: Path, title: str, port: str) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("w", encoding="utf-8")
        self.write_raw(f"# {title}\n")
        self.write_raw(f"# started={datetime.now().isoformat()}\n")
        self.write_raw(f"# port={port} baud={BAUD}\n\n")

    def write_raw(self, text: str) -> None:
        self.file.write(text)
        self.file.flush()

    def write_line(self, prefix: str, text: str) -> None:
        entry = f"[{line_ts()}] {prefix} {text}"
        print(entry)
        self.file.write(entry + "\n")
        self.file.flush()

    def close(self) -> None:
        self.write_raw(f"\n# ended={datetime.now().isoformat()}\n")
        self.file.close()


class PicoRig:
    def __init__(self, port: str, log: SessionLog, timeout: float = 0.2) -> None:
        self.port = port
        self.log = log
        self.ser = serial.Serial(port, BAUD, timeout=timeout)
        time.sleep(1.5)
        self._drain_startup()

    def close(self) -> None:
        self.ser.close()

    def _drain_startup(self) -> None:
        idle_deadline = time.monotonic() + 0.5
        while time.monotonic() < idle_deadline:
            line = self._readline()
            if line is None:
                continue
            self.log.write_line("<", line.text)

    def _readline(self) -> RigLine | None:
        raw = self.ser.readline()
        if not raw:
            return None
        text = raw.decode("utf-8", errors="replace").strip()
        if not text:
            return None
        return RigLine(line_ts(), text)

    def command(self, command: str, terminal: str | tuple[str, ...] = TERMINAL_PREFIXES, timeout: float = 10.0) -> list[str]:
        self.log.write_line(">", command)
        self.ser.write((command + "\n").encode("ascii"))
        self.ser.flush()

        deadline = time.monotonic() + timeout
        lines: list[str] = []
        while time.monotonic() < deadline:
            line = self._readline()
            if line is None:
                continue
            lines.append(line.text)
            self.log.write_line("<", line.text)
            if isinstance(terminal, tuple):
                if line.text.startswith(terminal):
                    break
            elif line.text.startswith(terminal):
                break
        else:
            raise TimeoutError(f"timeout waiting for Pico response to: {command}")

        if lines and lines[-1].startswith("ERR "):
            raise RuntimeError(lines[-1])
        return lines

    def command_until(self, command: str, end_line: str, timeout: float) -> list[str]:
        self.log.write_line(">", command)
        self.ser.write((command + "\n").encode("ascii"))
        self.ser.flush()

        deadline = time.monotonic() + timeout
        lines: list[str] = []
        while time.monotonic() < deadline:
            line = self._readline()
            if line is None:
                continue
            lines.append(line.text)
            self.log.write_line("<", line.text)
            if line.text.startswith("ERR "):
                raise RuntimeError(line.text)
            if line.text == end_line:
                return lines

        raise TimeoutError(f"timeout waiting for {end_line}: {command}")


def run_status(rig: PicoRig) -> None:
    rig.command("PING")
    rig.command("STATUS")


def run_monitor(rig: PicoRig, port: str, duration_ms: int) -> None:
    rig.command_until(f"MONITOR {port} {duration_ms}", "OK MONITOR END", timeout=(duration_ms / 1000) + 5)


def run_r34(rig: PicoRig, attempts: int, hold_delay: int, timeout_ms: int, post_ms: int) -> None:
    if hold_delay > 0:
        print(f"Hold SELECT now. Starting in {hold_delay}s.")
        time.sleep(hold_delay)

    rig.command("UART INT 2400")

    variants = [
        ("A5 01 01 A7", "legacy checksum candidate"),
        ("A5 01 01 02", "sum checksum candidate"),
    ]

    for attempt in range(1, attempts + 1):
        payload, label = variants[(attempt - 1) % len(variants)]
        rig.log.write_raw(f"\n# R34 attempt={attempt} payload={payload} label={label}\n")
        print(f"\nR34 attempt {attempt}/{attempts}: {label} [{payload}]")

        command = f"CYCLE_MARKER INT {timeout_ms} {post_ms} 41 FD F9 RESP {payload}"
        rig.command_until(command, "OK MARKER END", timeout=(timeout_ms + post_ms + 3000) / 1000)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control and log the UT33C+ Pico rig over USB serial.")
    parser.add_argument("--port", default=None, help="Pico serial port. Auto-detected if omitted.")
    parser.add_argument("--log-dir", default=str(LOG_DIR), help="Directory for run logs.")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Check firmware health and rig state.")

    monitor = sub.add_parser("monitor", help="Capture UART output from the rig.")
    monitor.add_argument("--meter-port", choices=["INT", "EXT", "BOTH"], default="BOTH")
    monitor.add_argument("--duration-ms", type=int, default=5000)

    r34 = sub.add_parser("r34", help="Run the precise marker-response experiment without reflashing.")
    r34.add_argument("--attempts", type=int, default=10)
    r34.add_argument("--hold-delay", type=int, default=5, help="Seconds to wait while you hold SELECT.")
    r34.add_argument("--timeout-ms", type=int, default=2000)
    r34.add_argument("--post-ms", type=int, default=1000)

    raw = sub.add_parser("cmd", help="Send one raw firmware command.")
    raw.add_argument("firmware_command", nargs=argparse.REMAINDER)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    port = args.port or find_pico_port()
    log_dir = Path(args.log_dir)
    log_path = log_dir / f"{args.command}_{now_label()}.log"

    log = SessionLog(log_path, f"UT33C+ Pico rig {args.command}", port)
    rig: PicoRig | None = None

    try:
        rig = PicoRig(port, log)

        if args.command == "status":
            run_status(rig)
        elif args.command == "monitor":
            run_monitor(rig, args.meter_port, args.duration_ms)
        elif args.command == "r34":
            run_r34(rig, args.attempts, args.hold_delay, args.timeout_ms, args.post_ms)
        elif args.command == "cmd":
            if not args.firmware_command:
                raise ValueError("cmd requires a firmware command")
            raw_command = " ".join(args.firmware_command)
            first_word = raw_command.split(maxsplit=1)[0].upper()
            if first_word in {"MARKER", "CYCLE_MARKER"}:
                rig.command_until(raw_command, "OK MARKER END", timeout=10)
            elif first_word == "MONITOR":
                rig.command_until(raw_command, "OK MONITOR END", timeout=10)
            else:
                rig.command(raw_command)

        print(f"\nLog saved to {log_path}")
        return 0
    except KeyboardInterrupt:
        print(f"\nInterrupted. Log saved to {log_path}")
        return 130
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        print(f"Log saved to {log_path}", file=sys.stderr)
        return 1
    finally:
        if rig is not None:
            rig.close()
        log.close()


if __name__ == "__main__":
    raise SystemExit(main())

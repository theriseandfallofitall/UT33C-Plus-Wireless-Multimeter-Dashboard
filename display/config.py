"""Display application configuration."""

from pathlib import Path


LOG_DIR = Path("logs")
SNAPSHOT_CSV = "snapshots.csv"
PICO_USB_BAUD = 115200
PICO_MONITOR_COMMAND = b"MONITOR INT 86400000\n"

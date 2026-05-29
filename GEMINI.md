# UT33C+ Wireless Dashboard Architecture

This repository is an operational Python application for wirelessly logging and displaying telemetry from the UT33C+ multimeter via a Bluetooth modification. 

**The hardware reverse-engineering phase is complete.** Do not attempt to find or execute UART command-injection vectors; they are locked behind OEM authorization. The 9-pad LCD matrix is purely for multiplexing display segments. The meter is treated strictly as a read-only telemetry source.

## Codebase Architecture
- **`app.py`:** The primary Tkinter UI dashboard. Handles asynchronous serial port auto-discovery, Bluetooth drop recovery (5s heartbeat), live graphing (matplotlib), and snapshot management.
- **`cli_logger.py`:** A headless, console-only alternative for pure CSV data acquisition.
- **`ut33c/decoder.py`:** The core protocol logic. Parses the continuous 2400 baud, 10-byte binary frames into structured `Reading` dataclasses.

## Conventions
- Always default to `2400` baud when interfacing with the UT33C+.
- Serial read loops must be non-blocking and robust against sudden Bluetooth disconnects.
- The UI must remain completely decoupled from the blocking serial read thread.

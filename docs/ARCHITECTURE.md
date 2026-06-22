# Project architecture

This is a small Python app for reading the UT33C+ multimeter's Bluetooth telemetry stream and showing it in a desktop dashboard.

The reverse engineering work is already done. The meter is treated as a read-only data source. Do not try to use the RX pad for remote control; the command path appears to require an OEM authorization sequence, and the LCD pad group is just display/keypad multiplexing.

## Main files

- `app.py`: Tkinter dashboard. Handles serial port discovery, Bluetooth reconnects, live graphing, and snapshots.
- `ut33c_logger.py`: command line logger for CSV capture without the GUI.
- `ut33c/decoder.py`: protocol decoder. Parses the 2400 baud, 10-byte frames into structured readings.
- `ut33c/ports.py`: serial/Bluetooth port discovery helpers.
- `ut33c/config.py`: local configuration helpers.

## Conventions

- Use 2400 baud for the UT33C+.
- Keep serial reads non-blocking so a Bluetooth dropout does not freeze the app.
- Keep the UI thread separate from serial I/O.
- Treat the meter as read-only. Hardware button bypasses are the safer route if remote control is ever needed.

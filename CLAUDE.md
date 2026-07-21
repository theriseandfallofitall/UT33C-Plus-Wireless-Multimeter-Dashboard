# CLAUDE.md

Python app that reads telemetry from a UNI-T UT33C+ multimeter over a Bluetooth/serial UART tap and shows it in a live dashboard. The meter is a **read-only** telemetry source — the reverse-engineering phase is done; do not hunt for UART command-injection / remote-control vectors (locked behind OEM auth, dead-ends documented in `docs/RESEARCH_HISTORY.md`).

## Run

```bash
pip install -r requirements.txt   # pyserial>=3.5, matplotlib>=3.8
python app.py                     # Tkinter dashboard
python ut33c_logger.py            # headless CSV logger
```
Both take `--port COMx`; auto-detect if omitted. Port auto-discovery: `ut33c/ports.py` matches description keywords (USB, FT232, PICO, CH340, CP210, "UT33C", ...).

## Layout
- `app.py` — Tkinter dashboard. Single `App(tk.Tk)` class. Blocking serial read runs in a daemon `threading.Thread` (`_read_serial_loop`); frames passed to UI via queue (`_process_queue`). Tabs: live, graph (matplotlib TkAgg), snapshots, settings. Has tear-off always-on-top overlay window and 5s Bluetooth-drop reconnect.
- `ut33c_logger.py` — headless console + CSV logger to `logs/`.
- `ut33c/decoder.py` — **core protocol logic**. Parses the 10-byte binary frames into `Reading` dataclasses. `pop_next_frame()` finds/validates frames in a rolling buffer; `decode_frame()` maps mode byte → scale/unit.
- `ut33c/ports.py` — serial-port discovery. `ut33c/config.py` — paths.

## Protocol (see `docs/PROTOCOL.md`)
- **2400 baud**, 10-byte frames: `AB CD ID MODE B0 B1 B2 B3 STATUS CS`. Header `\xAB\xCD`.
- Mode byte masked with `0x7F`; value = `frame[4:8]` big-endian signed. Checksum = `sum(frame[2:8]) & 0xFF == frame[9]`.
- Mode table (`MODES` dict) holds per-mode name/unit/scale; special transforms for Celsius→Fahrenheit and continuity/diode. `OL` (overload) handling is per-mode.

## Conventions
- Default to **2400 baud** for the UT33C+.
- Serial reads non-blocking and resilient to sudden Bluetooth disconnects; **UI thread stays decoupled from the serial read thread**.
- `decoder.py` is shared by both `app.py` and `ut33c_logger.py` — change protocol logic there, not in callers.

## Constraints
- Test rig uses a Pico whose firmware needs physical BOOTSEL re-flash — disruptive. Solve via the existing serial command interface before suggesting a firmware change. (see `MEMORY.md`)
- Safety: meter's internal ground ties to the COM probe — never USB-tether the meter to a grounded PC while measuring high voltage. Bluetooth mod gives galvanic isolation.

## Notes
- `GEMINI.md` is a parallel agent-guidance file; it references `cli_logger.py` but the actual headless script is `ut33c_logger.py`.
- `logs/*.{log,csv,txt}` are git-ignored; committed sample `.log` captures exist as protocol references.

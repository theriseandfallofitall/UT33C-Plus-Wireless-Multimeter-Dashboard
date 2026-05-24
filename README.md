# UNI-T UT33C+ UART Decode and Reverse Engineering

This repository contains the research notes, host tools, Pico firmware, and display tools used to decode the hidden UART telemetry stream from the UNI-T UT33C+ multimeter.

The project has two main parts:

- Reverse engineering: protocol discovery, hardware-in-the-loop rig control, raw captures, and research notes.
- On-screen display: live decoded readings, graphing, CSV logging, and snapshot capture.

The Pico code follows the same split:

- `pico/cpp/src/main.cpp`: passive UART passthrough firmware for direct display/logging workflows.
- `pico/cpp/firmware/main_rig_command.cpp`: serial-controlled rig firmware used for automated reverse-engineering experiments.

## Quick Start

Create a virtual environment and install the host dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```

### Direct UART logging

Use this when the meter is connected through a USB-serial adapter, or through the Pico passthrough firmware:

```bash
python -m tools.final_logger
```

### Big-screen display

Use the direct display for a normal 2400 baud UART stream:

```bash
python -m display.big_screen_direct
```

Use the rig display only when the Pico is running the command rig firmware:

```bash
python -m display.big_screen_rig
```

### Automated reverse-engineering rig

The automated rig uses the command firmware and `tools/pico_rig_runner.py`:

```bash
python -m tools.pico_rig_runner status
python -m tools.pico_rig_runner monitor --meter-port BOTH --duration-ms 5000
python -m tools.pico_rig_runner r34
```

Build and deploy Pico firmware from the project root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deploy_pico.ps1
```

See [docs/PICO_GUIDE.md](docs/PICO_GUIDE.md) before flashing, because only one Pico firmware profile should be active at a time.

## Repository Layout

| Path | Purpose |
| :--- | :--- |
| `ut33c/` | Shared Python package for protocol decoding and frame parsing. |
| `display/` | Self-contained on-screen display workflow: apps, display config, port discovery, protocol wrapper, launch scripts, and display dependencies. |
| `tools/` | Operational host tools for logging, capture, experimental control, and Pico rig control. |
| `pico/cpp/` | PlatformIO firmware project for the Pico. |
| `pico/micropython/` | Earlier MicroPython rig experiments. |
| `research/` | Focused discovery scripts and fuzzing tools. |
| `legacy/` | Older scripts retained for historical context. |
| `docs/` | Protocol, hardware, wiring, status, and testing notes. |
| `docs/README.md` | Documentation index. |
| `tests/` | Decoder regression tests using captured fixture logs. |
| `logs/` | Captured local logs and curated decoder fixtures. |

## Current Findings

- The meter emits 10-byte `AB CD` frames at 2400 baud.
- The likely chipset family is SDIC/Jinghua SD7501 or a close variant.
- Passive telemetry decoding is working for voltage, current, resistance, continuity, diode, and temperature modes.
- Remote mode switching was investigated heavily, but no usable command unlock was found. The diagnostic path appears to require a physical button state plus an unknown authorization key.

See [docs/STATUS.md](docs/STATUS.md), [docs/PROTOCOL_MAP.md](docs/PROTOCOL_MAP.md), and [docs/TESTING_HISTORY.md](docs/TESTING_HISTORY.md) for the full research record.

## Safety Warning

The internal UART ground is electrically connected to the meter COM lead. Do not connect the meter to high voltage while it is wired to a grounded PC or Pico USB connection unless you have proper isolation.

# UT33C+ UART Decode & Rig Control

This repository contains a suite of tools for decoding and interacting with the hidden UART telemetry stream from **UNI-T UT33C+** digital multimeters.

## Core Features
- **Real-time Decoding:** Fully mapped 2400 baud binary protocol for DCV, ACV, Resistance, Continuity, and Temperature.
- **On-Screen Display:** Live UI with graphing, CSV logging, and snapshot capture.
- **Automated Rig Control:** C++ firmware for the Pi Pico (YD-RP2040) to automate resets, monitoring, and diagnostic probing.
- **Hardware Mapping:** Detailed mapping of internal pads, including the LCD/Keypad matrix.

## Hardware Setup
See [docs/HARDWARE_SPEC.md](docs/HARDWARE_SPEC.md) for pad locations and wiring.
- **Internal UART:** Primary telemetry stream (2400 8N1).
- **Reset Pads:** Pad 1 (Soft) and Pad 2 (Hard) for bootloader access.
- **Matrix Pads:** LCD segment and button scanning interface.

## Quick Start

### 1. Flash the Pico
The definitive firmware is the C++ Rig Command build.
1.  Open `pico/cpp/` in PlatformIO.
2.  Copy `pico/cpp/firmware/main_rig_command.cpp` to `pico/cpp/src/main.cpp`.
3.  Flash to your Pico.

### 2. Launch the Display
For a real-time graphical interface:
```bash
# Using the Pico Rig (115200 baud USB)
python -m display.big_screen_rig

# Using a direct USB-TTL or Passthrough (2400 baud)
python -m display.big_screen_direct
```

### 3. Data Logging
To log telemetry to CSV without the UI:
```bash
python -m tools.final_logger
```

## Documentation
- [docs/PROTOCOL_MAP.md](docs/PROTOCOL_MAP.md) - Frame structure and range bytes.
- [docs/STATUS.md](docs/STATUS.md) - Project status and major discoveries.
- [docs/HARDWARE_SPEC.md](docs/HARDWARE_SPEC.md) - Final pad and wiring specification.

## Safety Warning
Internal GND = Meter COM. Use opto-isolation for high-voltage measurements. This project is for educational reverse-engineering purposes.

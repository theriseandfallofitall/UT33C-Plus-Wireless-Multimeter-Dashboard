# UNI-T UT33C+ UART Decode & Reverse Engineering

This repository contains the full research and toolset for decoding the hidden high-speed UART telemetry stream from the UNI-T UT33C+ multimeter.

---

## ⚡ Quick Start

### 1. Monitor & Log (PC Side)
If you have the multimeter connected to your PC via an FTDI or USB-Serial adapter, use the final decoded logger:
```bash
python ut33c_plus_final_logger.py
```
*Supports: Voltage, Current, Resistance, Continuity, Celsius, Fahrenheit.*

### 2. Automated Testing (Pi Pico 2)
If you are building the automated test rig using a Raspberry Pi Pico 2:
- **Firmware:** Located in `pico/cpp/` (PlatformIO) or `pico/micropython/`.
- **Wiring:** See [docs/PICO_WIRING.md](docs/PICO_WIRING.md).
- **Guide:** See [docs/PICO_GUIDE.md](docs/PICO_GUIDE.md).

---

## 📁 Repository Structure

### 🛠 Tools
*   `ut33c_plus_final_logger.py`: The primary high-level decoder and CSV logger.
*   `ut33c_raw_capture.py`: Utility for capturing raw hex frames for new modes.

### 📂 Subdirectories
*   `docs/`: Full technical documentation, protocol maps, and wiring guides.
*   `pico/`: All firmware for the automated Pi Pico 2 hardware rig (C++ and MicroPython).
*   `research/`: Discovery scripts used for baud sweeps, brute-forcing, and reset monitoring.
*   `legacy/`: Older scripts and initial investigation attempts.
*   `logs/`: Storage for captured session data and CSV logs.

---

## 📝 Technical Documentation Links
- **[Latest Project Status](docs/STATUS.md)** - Where we left off and current blockers.
- **[Protocol Specification](docs/PROTOCOL_MAP.md)** - Detailed 10-byte frame breakdown.
- **[Hardware Specification](docs/HARDWARE_SPEC.md)** - Detailed rig components and logic.

---

## ⚠️ Safety Warning
The internal UART ground is electrically connected to the meter's **COM** lead. **NEVER** connect the meter to a grounded PC while measuring high voltage without opto-isolation.

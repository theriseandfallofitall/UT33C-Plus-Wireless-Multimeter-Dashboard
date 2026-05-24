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

### 2. Automated Testing (YD-RP2040)
If you are building the automated test rig:
- **Firmware:** Located in `pico/cpp/` (PlatformIO).
- **Deployment:** Use `.\deploy_pico.ps1` once to build and upload the serial-controlled rig firmware.
- **Testing:** Use `python pico_rig_runner.py status`, `python pico_rig_runner.py monitor`, or `python pico_rig_runner.py r34` to run experiments without reflashing.
- **Wiring:** See [docs/HARDWARE_SPEC.md](docs/HARDWARE_SPEC.md).

---

## 🚀 Research & Discoveries

### 🧠 Chipset Identification
The meter has been identified as likely using the **SDIC SD7501** SoC. This is based on its unique 10-byte UART protocol and 2400 baud telemetry.

### 🔓 Diagnostic Gateway (State 41)
We discovered a hidden diagnostic state (**Protocol ID 41**) in earlier reset/null-burst work. The current serial-controlled Pico workflow has mapped the hard-power boot markers across modes; the strongest remaining route is the very early external `F9` window seen with only the HOLD/SELECT button held in Continuity. The combined HOLD/SELECT + Backlight test did not reproduce `F9`, and the device OFF state was silent. See the [Mode Change Plan](docs/MODE_CHANGE_PLAN.md) and [Testing History](docs/TESTING_HISTORY.md).

---

## 📁 Repository Structure

### 🛠 Tools
*   `ut33c_plus_final_logger.py`: The primary high-level decoder and CSV logger.
*   `fuzzer_monitor.py`: Long-duration stream logger for the automated rig.
*   `ut33c_raw_capture.py`: Utility for capturing raw hex frames for new modes.
*   `deploy_pico.ps1`: Automated build and upload script for the RP2040.
*   `pico_rig_runner.py`: Host-side controller for repeatable Pico rig tests over USB serial.

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

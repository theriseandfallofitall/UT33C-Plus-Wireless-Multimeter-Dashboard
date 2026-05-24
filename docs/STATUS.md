# Project Status: UT33C+ UART Decode
**Last Updated: May 24, 2026**

## 🎯 Current Status
The project has successfully transitioned to an **automated hardware-in-the-loop (HIL) fuzzer rig**. We are now performing long-duration discovery to unlock bidirectional (RX) control.

## 🏆 Major Discoveries
1.  **Raw Telemetry Port:** Stable 2400 baud stream confirmed on internal pads.
2.  **ADC Protocol:** Decoded 10-byte binary frames. 
    *   **Checksum:** `sum(Bytes 2..7) & 0xFF` (Verified).
    *   **Value:** Signed 32-bit big-endian ADC counts.
3.  **Power Sequencing:** Discovered that a clean power cycle requires an **inverted dual-rail cut**:
    *   **Positive Rail:** Active HIGH (3.3V).
    *   **GND Rail:** Active LOW (GND).
4.  **Hardware Rig:** Successfully deployed on a **YD-RP2040** board. The rig now handles power-on resets, baud rate sweeps, and rapid command injection.
5.  **Stream Logging:** Implemented `fuzzer_monitor.py` for structured, timestamped session logging of fuzzer events and telemetry.

## 🚧 Challenges & Blockers
*   **RX Lock:** The meter's RX line is currently non-responsive. We are fuzzing common UNI-T sync sequences (`AB 01`, `AB 00`) during the post-reset boot window.
*   **Opto-Port Noise:** The external opto-port remains much noisier than the internal pads, but is being monitored simultaneously.

## 📍 Where We Left Off
The YD-RP2040 is running the Phase 1 (Baud) and Phase 2 (Injection) loops. `fuzzer_monitor.py` is active and logging all interactions to `logs/fuzzer_runs/` for future AI analysis.

---
## ⚠️ Update (May 23, 2026)
The C++ firmware (`pico/cpp/src/main.cpp`) was found to be a basic "hello world" serial test, not the advanced fuzzer described in some documents. The fuzzing logic needs to be implemented.

## 📂 Key Files
*   `ut33c_plus_final_logger.py`: The production PC tool for logging data.
*   `src/main.cpp`: The PlatformIO C++ fuzzer logic for the Pico 2.
*   `PICO_WIRING.md`: Detailed wiring for the automated rig.
*   `PROTOCOL_MAP.md`: Detailed breakdown of hex codes and formulas.

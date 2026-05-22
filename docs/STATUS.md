# Project Status: UT33C+ UART Decode
**Last Updated: May 22, 2026**

## 🎯 Current Status
The project has successfully reverse-engineered the raw data stream from the UNI-T UT33C+ internal debug pads. We have shifted from the legacy opto-port to a high-speed, auto-transmitting internal UART interface.

## 🏆 Major Discoveries
1.  **Raw Telemetry Port:** Identified internal pads that auto-transmit raw ADC counts at **2400 baud**.
2.  **ADC Protocol:** Decoded the 10-byte binary frame structure, including mode detection and value scaling.
3.  **Reset Logic:** 
    *   **Pad 2** is a Hard Reset (CPU Halt).
    *   **Pad 1** is a Soft Reset (Initializes Logic/Buzzer).
4.  **Hardware Rig:** Developed a Pi Pico 2 (RP2350) automated rig that can power-cycle the meter, trigger resets, and monitor both UART ports simultaneously.

## 🚧 Challenges & Blockers
*   **Bidirectional Control:** The multimeter's RX line currently appears to ignore all incoming commands. The port seems to be firmware-locked to "Transmit Only" for measurement data.
*   **Bootloader Access:** Brute-force command injection during the reset window has not yet revealed a hidden command shell or programming mode.

## 📍 Where We Left Off
The Pi Pico 2 rig is built and verified with C++. We have a serial heartbeat working on the RP2350. The next logical step is to run long-duration fuzzing cycles to see if any specific timing or character combination can unlock the RX line.

---

## 📂 Key Files
*   `ut33c_plus_final_logger.py`: The production PC tool for logging data.
*   `src/main.cpp`: The PlatformIO C++ fuzzer logic for the Pico 2.
*   `PICO_WIRING.md`: Detailed wiring for the automated rig.
*   `PROTOCOL_MAP.md`: Detailed breakdown of hex codes and formulas.

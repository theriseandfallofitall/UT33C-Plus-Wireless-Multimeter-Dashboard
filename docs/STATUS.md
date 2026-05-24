## 🎯 Current Status
The project has successfully transition to a **Data-Driven Automated HIL Rig**. We have identified a specific firmware gateway (State 41) for bidirectional control and verified the physical integrity of the RX link.

## 🏆 Major Discoveries (May 24, 2026)
1.  **State 41 Unlock:** Discovered that a **NULL burst** during Soft Reset locks the MCU into Protocol ID `41` (Awaiting Command). This is our primary target for future "handshake" attempts.
2.  **Physical Proof:** Confirmed that RX injections cause measurable reflections on the TX line, proving the electrical path to the MCU is valid.
3.  **Inverted Dual-Rail Power:** Perfected the power-cycling logic required to fully clear internal MCU and ADC registers.
4.  **Baud Rate Filter:** Verified that the meter ignores 9600 and 115200 baud, suggesting the "Factory Unlock" sequence is natively **2400 baud**.

## 🧠 Core Assumptions (For Handoff)
*   **Assumption 1:** State `41` is a "Bootloader Idle" state. It expects a specific multi-byte sequence (likely ASCII) to transition into a "Diagnostic" or "EEPROM Read" state.
*   **Assumption 2:** The meter uses a 2400 baud fixed bitrate even for its diagnostic shell (highly unusual, but supported by current data).
*   **Assumption 3:** Pad 1 (Soft Reset) is the most reliable entry point as it keeps the UART peripheral energized.

## 📝 TODO: Next Research Phase
*   [ ] **R12: Long NULL Blast (10s):** Hold RX low for 10+ seconds to see if a Watchdog Timeout triggers a "Recovery Mode."
*   [ ] **R13: EEPROM Address Fuzz:** Inject sequences like `READ 0000`, `READ 0001` inside the State 41 window.
*   [ ] **R14: Double-Reset Glitch:** Rapidly pulse Pad 1 twice (<10ms) to bypass the `81 -> 01` boot transition.
*   [ ] **R15: High-Side Jitter:** Vary the Power-ON delay (50ms to 500ms) while blasting `55 AA` to find the exact opcode fetch window.

## 📍 Where We Left Off
The YD-RP2040 rig is running the latest C++ fuzzer. All discovery runs (R01-R11) are logged in `docs/TESTING_HISTORY.md` and `logs/fuzzer_runs/`. The "Door" is open (State 41), we just need the "Key."

---
## ⚠️ Update (May 23, 2026)
The C++ firmware (`pico/cpp/src/main.cpp`) was found to be a basic "hello world" serial test, not the advanced fuzzer described in some documents. The fuzzing logic needs to be implemented.

## 📂 Key Files
*   `ut33c_plus_final_logger.py`: The production PC tool for logging data.
*   `src/main.cpp`: The PlatformIO C++ fuzzer logic for the Pico 2.
*   `PICO_WIRING.md`: Detailed wiring for the automated rig.
*   `PROTOCOL_MAP.md`: Detailed breakdown of hex codes and formulas.

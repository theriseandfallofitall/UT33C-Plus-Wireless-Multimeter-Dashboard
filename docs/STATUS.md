## 🎯 Current Status
The project has successfully transition to a **Data-Driven Automated HIL Rig**. We have identified a specific firmware gateway (State 41) for bidirectional control and verified the physical integrity of the RX link.

## 🏆 Major Discoveries (May 24, 2026)
1.  **State 41 Unlock:** Discovered that a **NULL burst** during Soft Reset locks the MCU into Protocol ID `41` (Awaiting Command). This is our primary target for future "handshake" attempts.
2.  **Physical Proof:** Confirmed that RX injections cause measurable reflections on the TX line, proving the electrical path to the MCU is valid.
3.  **Physical Button Mandatory:** Found that entering diagnostic mode requires holding a physical button (SELECT or HOLD) during the reset sequence. Without it, the MCU ignores all UART injection.
4.  **Early Boot Markers:** Identified `E0` and `AB FD` markers occurring immediately after a hard power-on reset, providing a target window for early sync.
5.  **Inverted Dual-Rail Power:** Perfected the power-cycling logic required to fully clear internal MCU and ADC registers.

## 🧠 Core Assumptions (For Handoff)
*   **Assumption 1:** The chipset is an **SDIC SD7501** (or close variant).
*   **Assumption 2:** State `41` is a "Bootloader Ready" signal (ASCII 'A').
*   **Assumption 3:** The command gateway requires the **`0xA5`** binary prefix.

## 🚀 Mode Change Roadmap
We have shifted from general fuzzing to a targeted protocol attack. The new goal is to achieve **Remote Mode Switching** (e.g., dial is on Continuity, but UART forces it to 20V DC).
- **Strategy Document:** [docs/MODE_CHANGE_PLAN.md](docs/MODE_CHANGE_PLAN.md)

## 📝 TODO: Next Research Phase
*   [x] **R32: EEPROM Read Discovery:** Attempted with Soft Reset; failed to trigger markers reliably.
*   [x] **R33: Hard-Power Button Handshake:** Discovered `AB FD` marker consistently appears ~1.2s after power-on when SELECT is held.
*   [ ] **R34: Precise Marker Response:** Extend detection window to 2s, wait for `AB FD` or `41`, and inject `0xA5 0x01 0x01`.

## 📍 Where We Left Off
The YD-RP2040 rig is running the latest C++ fuzzer. All discovery runs (R01-R11) are logged in `docs/TESTING_HISTORY.md` and `logs/fuzzer_runs/`. The "Door" is open (State 41), we just need the "Key."

---

## 📂 Key Files
*   `ut33c_plus_final_logger.py`: The production PC tool for logging data.
*   `src/main.cpp`: The PlatformIO C++ fuzzer logic for the Pico 2.
*   `PICO_WIRING.md`: Detailed wiring for the automated rig.
*   `PROTOCOL_MAP.md`: Detailed breakdown of hex codes and formulas.

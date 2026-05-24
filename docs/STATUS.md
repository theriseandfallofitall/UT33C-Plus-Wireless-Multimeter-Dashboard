## 🎯 Current Status
The project has successfully transition to a **Data-Driven Automated HIL Rig**. We have identified a specific firmware gateway (State 41) for bidirectional control and verified the physical integrity of the RX link.

## 🏆 Major Discoveries (May 24, 2026)
1.  **State 41 Unlock:** Discovered that a **NULL burst** during Soft Reset locks the MCU into Protocol ID `41` (Awaiting Command). This is our primary target for future "handshake" attempts.
2.  **Physical Proof:** Confirmed that RX injections cause measurable reflections on the TX line, proving the electrical path to the MCU is valid.
3.  **Physical Button Mandatory:** Found that entering diagnostic mode requires holding the physical HOLD/SELECT button during the reset sequence. Without it, the MCU ignores all UART injection.
4.  **Early Boot Markers:** Identified `E0` and `AB FD` markers occurring immediately after a hard power-on reset, providing a target window for early sync.
5.  **Inverted Dual-Rail Power:** Perfected the power-cycling logic required to fully clear internal MCU and ADC registers.
6.  **Mode/Button-Dependent External Marker:** Confirmed the external/opto UART emits `AB ED` in Continuity with no held button, but `AB FD` in other characterized modes and in Continuity when HOLD/SELECT is held.
7.  **2000mV Range Byte:** Confirmed 2000mV mode uses range byte `07`.
8.  **Fast Marker Injection:** Updated Pico firmware to transmit response bytes before USB logging on marker match.
9.  **200V Range Byte:** Confirmed 200V mode uses range byte `15`.
10. **600V Range Byte:** Confirmed 600V mode uses range byte `18`.
11. **600VAC Range Byte:** Confirmed 600VAC mode uses range byte `11`.
12. **200VAC Range Byte:** Confirmed 200VAC mode uses range byte `12`.
13. **Celsius Range Byte:** Confirmed Celsius mode uses range byte `16`.
14. **Button-State Marker Dependency:** Holding the HOLD/SELECT button in Continuity changed the external/opto marker from earlier no-button `AB ED` to `AB FD`.
15. **Button-Held Early F9:** Passive HOLD/SELECT-held Continuity capture reproduced an early external `F9` before `E0` and `AB FD`.
16. **Combined Button State:** Holding HOLD/SELECT plus Backlight in Continuity produced mixed external `AB ED`/`AB FD` markers and did not reproduce early `F9`.
17. **OFF State Is Silent:** Device OFF with HOLD/SELECT plus Backlight held produced no UART output on either channel.

## 🧠 Core Assumptions (For Handoff)
*   **Assumption 1:** The chipset is an **SDIC SD7501** (or close variant).
*   **Assumption 2:** State `41` is a "Bootloader Ready" signal (ASCII 'A').
*   **Assumption 3:** The command gateway requires the **`0xA5`** binary prefix.

## 🚀 Mode Change Roadmap
We have shifted from general fuzzing to a targeted protocol attack. The new goal is to achieve **Remote Mode Switching** (e.g., dial is on Continuity, but UART forces it to 20V DC).
- **Strategy Document:** [docs/MODE_CHANGE_PLAN.md](docs/MODE_CHANGE_PLAN.md)

## 📝 TODO: Next Research Phase
*   [x] **R32: EEPROM Read Discovery:** Attempted with Soft Reset; failed to trigger markers reliably.
*   [x] **R33: Hard-Power Button Handshake:** Discovered `AB FD` marker consistently appears ~1.2s after power-on when the HOLD/SELECT button is held.
*   [x] **R34: Precise Marker Response:** Detected `FD` reliably and injected `0xA5 0x01 0x01`; no ACK or mode change.
*   [x] **R35-R42: Command Sweeps:** Tested A5, legacy AB, full-frame, direct-range, and host-driven NULL paths; all neutral.
*   [x] **R43-R45: External Marker Analysis:** Confirmed external/opto marker is `AB ED` in Continuity mode with no held button.
*   [x] **R46-R49: 200mV Mode Tests:** Confirmed `01 17` telemetry and discovered the external marker changes to `AB FD` in 200mV mode. Command probes remained neutral.
*   [x] **R50-R53: 2000mV Mode Tests:** Confirmed `01 07` telemetry. Internal marker was `FD`; external marker was mostly `FD` with occasional `ED` during command probes. Command probes remained neutral.
*   [x] **R54-R57: 20V Mode Tests:** Confirmed `01 0D` telemetry and `AB FD` on both channels using the faster injection firmware. Command probes remained neutral.
*   [x] **R58-R61: 200V Mode Tests:** Confirmed `01 15` telemetry and `AB FD` on both channels. Command probes remained neutral.
*   [x] **R62-R65: 600V Mode Tests:** Confirmed `01 18` telemetry and `AB FD` on both channels. Command probes remained neutral.
*   [x] **R66-R69: 600VAC Mode Tests:** Confirmed `01 11` telemetry and `AB FD` on both channels. Command probes remained neutral.
*   [x] **R70-R73: 200VAC Mode Tests:** Confirmed `01 12` telemetry and `AB FD` on both channels. Command probes remained neutral.
*   [x] **R74-R77: Celsius Mode Tests:** Confirmed `01 16` telemetry and `AB FD` on both channels. Open temperature input repeated `AB CD 01 16 00 00 FF 7F 01 95`; command probes remained neutral.
*   [x] **R78-R80: HOLD/SELECT-Held Continuity Tests:** Confirmed button-held Continuity external marker is `AB FD`; no `41`, `F9`, or `81` appeared. FD and early-E0 command probes remained neutral.
*   [x] **R81-R83: HOLD/SELECT-Held Continuity Repeat:** Repeated the same physical-button condition; passive early capture showed `FF`, `F0`, and `F9` before `E0`. Stopped at `F9` discovery.
*   [x] **R84: HOLD/SELECT + Backlight Continuity Test:** Ten passive full power cycles showed internal `AB FD` every time, external mixed `AB ED`/`AB FD`, and no early `F9`.
*   [x] **R85: Device OFF + Both Buttons Test:** Five passive full power restores produced no internal or external UART output. Rig power was returned to OFF after the test.

## 📍 Where We Left Off
The YD-RP2040 rig is running the serial-controlled C++ firmware. Runs through R85 are logged in `docs/TESTING_HISTORY.md` and `logs/rig_runs/`. The best current next step remains a HOLD/SELECT-only Continuity capture of the external/opto UART first 0-100ms window to prove whether the early `F9` is repeatable before injecting after it.

---

## 📂 Key Files
*   `ut33c_plus_final_logger.py`: The production PC tool for logging data.
*   `pico_rig_runner.py`: Host-side controller for repeatable Pico rig tests.
*   `pico/cpp/src/main.cpp`: Serial-controlled PlatformIO C++ firmware for the Pico rig.
*   `docs/PICO_WIRING.md`: Detailed wiring for the automated rig.
*   `docs/PROTOCOL_MAP.md`: Detailed breakdown of hex codes and formulas.

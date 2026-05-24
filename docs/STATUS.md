## 🎯 Current Status
**Reverse-Engineering Concluded.** The project has successfully mapped the UART telemetry protocol and identified the hardware requirements and timing for the diagnostic bootloader gateway. However, after exhaustive autonomous multi-baud fuzzing, we have concluded that remote mode switching is locked behind an unknown (likely multi-byte) authorization key.

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
15. **Button-Held Early F9:** Passive HOLD/SELECT-held Continuity capture reproduced an early external `F9` before `E0` and `AB FD`. However, subsequent R86-R89 attempts were unable to repeat it reliably, suggesting it depends on specific power-rail decay states.
16. **Combined Button State:** Holding HOLD/SELECT plus Backlight in Continuity produced mixed external `AB ED`/`AB FD` markers and did not reproduce early `F9`.
17. **OFF State Is Silent:** Device OFF with HOLD/SELECT plus Backlight held produced no UART output on either channel.
18. **Firmware Command: RESET_MARKER:** Added a new command to the Pico rig to eliminate USB latency when watching for boot markers immediately after a soft or hard reset.
19. **Discharge Delay Requirement:** Discovered that a **5-second** dual-rail power-off delay is necessary for a "True Zero" reset of the MCU and ADC registers.
20. **Handshake Lockout:** Exhaustive autonomous fuzzing (R91) proved that standard single-byte or full-frame payloads injected immediately after the boot marker at any standard baud rate will not unlock the device.

## 🧠 Core Assumptions (For Handoff)
*   **Assumption 1:** The chipset is an **SDIC SD7501** (or close variant).
*   **Assumption 2:** State `41` is a "Bootloader Ready" signal (ASCII 'A').
*   **Assumption 3:** The command gateway requires the **`0xA5`** binary prefix followed by an unknown OEM password.

## 🚀 Mode Change Roadmap
Active fuzzing for remote mode switching has been suspended. The protocol mapping is complete enough for passive telemetry logging.

## 📝 TODO: Next Research Phase
*   [x] **R84: HOLD/SELECT + Backlight Continuity Test:** Ten passive full power cycles showed internal `AB FD` every time, external mixed `AB ED`/`AB FD`, and no early `F9`.
*   [x] **R85: Device OFF + Both Buttons Test:** Five passive full power restores produced no internal or external UART output. Rig power was returned to OFF after the test.
*   [x] **R86-R89: F9 Repeatability Tests:** Attempted to repeat early external `F9` with HOLD/SELECT held and varied discharge delays; `F9` did not recur.
*   [x] **R90: Soft-Reset (Pad 1) Boot Window Test:** Pulsing Pad 1 while power was ON skipped the early boot markers entirely.
*   [x] **R91: Autonomous Multi-Baud Sweep:** Completed 810 permutations of zero-latency payload injections at 2400, 9600, and 115200 baud. All attempts failed to trigger a mode switch.

## 📍 Where We Left Off
The project is currently wrapped up. The 10-byte telemetry protocol is mapped and documented. The YD-RP2040 rig firmware is stable and supports zero-latency marker detection (`CYCLE_MARKER` / `RESET_MARKER`). The diagnostic bootloader exists and requires physical button holding, but the software key to unlock it remains unknown. Future attempts would likely require capturing a factory logic analyzer trace or performing sophisticated fault injection (voltage glitching) to bypass the password check.

---

## 📂 Key Files
*   `ut33c_plus_final_logger.py`: The production PC tool for logging data.
*   `pico_rig_runner.py`: Host-side controller for repeatable Pico rig tests.
*   `pico/cpp/src/main.cpp`: Serial-controlled PlatformIO C++ firmware for the Pico rig.
*   `docs/PICO_WIRING.md`: Detailed wiring for the automated rig.
*   `docs/PROTOCOL_MAP.md`: Detailed breakdown of hex codes and formulas.

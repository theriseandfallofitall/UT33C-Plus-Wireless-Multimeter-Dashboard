# UT33C+ Automated Testing History (HIL Rig)
Detailed chronological record of every automated discovery run executed on the YD-RP2040 Rig.

---

## 📊 Discovery Run Matrix

| Run ID | Meter Mode | Reset Trigger | Strategy | Discovery / Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R01** | 20V DC | Pad 2 (Hard) | Deep Fuzz (AB 00-FF) | Found **Protocol ID 81** (Boot) & **0x80 Mode Bit** (Diagnostic flag). | ✅ Success |
| **R02** | 10A DC | Pad 2 (Hard) | Deep Fuzz (AB 00-FF) | Confirmed dynamic boot signature (`81 0B`). Mapped 10A payloads. | ✅ Success |
| **R03** | Continuity | Pad 2 (Hard) | Deep Fuzz (AB 00-FF) | Verified `7F` hardware check artifact in Continuity boot firmware. | ✅ Success |
| **R04** | Continuity | Pad 1 (Soft) | Deep Fuzz (AB 00-FF) | Verified Pad 1 Soft Reset provides identical UART window to Pad 2. | ✅ Success |
| **R05** | Continuity | Pad 1 (Soft) | Burst Library | **MAJOR BREAKTHROUGH:** Discovered **Protocol ID 41** after 8x NULL burst. | ✅ Success |
| **R06** | Continuity | Pad 1 (Soft) | NULL Hold (2s) | **STABILIZATION SUCCESS:** Confirmed ID 41 persists as long as RX is low. | ✅ Success |
| **R08** | Continuity | Pad 1 (Soft) | State 41 Deep Fuzz | Tested 256 bytes *inside* State 41. No secondary transition triggered. | ✅ Success |
| **R09** | Continuity | Pad 1 (Soft) | State 41 Burst | Tested strings (`FACTORY`, `READ`) inside State 41. Injections received but ignored. | ✅ Success |
| **R10** | Continuity | Pad 1 (Soft) | Multi-Baud (9k6) | Meter ignored 9600 baud data. No change to standard boot loop. | ✅ Neutral |
| **R11** | Continuity | Pad 1 (Soft) | Multi-Baud (115k) | Meter ignored 115200 baud data. Confirmed native 2400 baud filter. | ✅ Neutral |
| **R12** | Continuity | Pad 1 (Soft) | Long NULL (10s) | No Watchdog "Recovery Mode" triggered. MCU eventually reboots to standard. | ✅ Neutral |
| **R13** | Continuity | Pad 1 (Soft) | EEPROM Probing | **SIGNAL ACQUIRED:** Triggered State 41 at Address 1 offset. State was transient. | ✅ Success |
| **R14** | Continuity | Pad 1 (Soft) | Double-Reset | Pulsed Pad 1 with 5ms gap. No bootloader bypass observed. | ✅ Neutral |
| **R15** | Continuity | Pad 1 (Soft) | High-Side Jitter | Varied PWR-ON delay (50-500ms). Target window missed or non-existent. | ✅ Neutral |
| **R16** | Continuity | Pad 1 (Soft) | NULL Sustainer | Blasted NULLs continuously. Confirmed State 41 drops out regardless of RX activity. | ✅ Success |
| **R17** | Continuity | Pad 1 (Soft) | Precise Injection | Sent `FACTORY`, `HELP` immediately after trigger. MCU ignored all commands. | ✅ Success |
| **R18** | Continuity | Pad 1 (Soft) | Timing Slide | Tested 0-20ms delay for `FACTORY` injection. State 41 remains locked/ignored. | ✅ Success |
| **R19** | Continuity | Pad 1 (Soft) | Trigger Fuzz | Varied inter-byte trigger speed (1-10ms). No change in stability. | ✅ Success |
| **R20** | Continuity | Pad 1 (Soft) | Stabilization | Tested variable post-trigger delays (10-200ms). Gateway is timing-critical. | ✅ Success |
| **R21** | Continuity | Pad 1 (Soft) | The A5 Unlock | Sent 0xA5 after NULLs. Failed to detect 0x41 gateway in time. | ✅ Neutral |
| **R24** | Continuity | Pad 1 (Soft) | Trigger Sweep | Tested variable NULL counts and delays. Gateway not detected. | ✅ Neutral |
| **R25** | Continuity | Pad 1 (Soft) | Hold/Select & Reset | User held the HOLD/SELECT button. Discovered new markers (`AB CD F9` and `AB CD 81`). | ✅ Success |
| **R26** | Continuity | Pad 1 (Soft) | Real-time Handshake | Monitored for non-standard bytes to send 0xA5. Failed. | ✅ Neutral |
| **R27** | Continuity | Pad 1 (Soft) | Auto Discovery | Swept parameters without physical button. Confirmed physical interaction is mandatory for diagnostic entry. | ✅ Success |
| **R28** | Continuity | Pad 1 (Soft) | Targeted Physical | Sent 16x NULL + 0xA5 while holding the HOLD/SELECT button. No ACK received. | ✅ Neutral |
| **R29** | Continuity | Pad 1 (Soft) | Gateway Probe | Very short 10ms reset pulse, sliding delay before NULLs. Gateway not triggered. | ✅ Neutral |
| **R30** | Continuity | Pad 2 (Hard) | Hard-Power Glitch | Power cycled the MCU. Detected `E0` and `AB FD` markers confirming early boot window access. | ✅ Success |
| **R31** | Continuity | Pad 2 (Hard) | Pre-Power Sync | Blasted `0x55 0xAA` before power-on. Still received `FE` and `AB FD`. | ✅ Success |
| **R32** | Continuity | Pad 1 (Soft) | EEPROM Read | Sent `0xA5 0x00` after boot marker. Soft Reset failed to trigger markers reliably in loop. | ✅ Neutral |
| **R33** | Continuity | Pad 2 (Hard) | Hard-Power Handshake | Sent NULLs after hard reboot while holding the HOLD/SELECT button. Discovered `AB FD` marker consistently appears ~1.2s after power-on. | ✅ Success |
| **R34** | Continuity | Dual-rail power cycle | Precise Marker Response | New serial-controlled Pico firmware detected `FD` on 10/10 attempts at ~1.11s after power-on and injected `A5 01 01 A7` / `A5 01 01 02`; no ACK or mode-byte change observed. | ✅ Neutral |
| **R35** | Continuity | Dual-rail power cycle | Command Candidate Sweep | Tested `A5`, `55`, `06`, `A5 00 00`, virtual button candidates, and direct mode candidates after `FD`; all returned to unchanged `AB CD 01 19 00 00 7F 00 00 99` telemetry. | ✅ Neutral |
| **R36** | Continuity | Dual-rail power cycle | Early `E0` Injection | Injected `A5`, `55`, `06`, `A5 00 00`, button, and direct-mode candidates immediately after `E0`; later `AB FD` still appeared and no telemetry change followed. | ✅ Neutral |
| **R37** | Continuity | Dual-rail power cycle | Inter-byte `AB` Injection | Injected between `AB` and `FD`; `FD` still arrived 10-16ms later and normal `01 19` telemetry resumed. | ✅ Neutral |
| **R38** | Continuity | Dual-rail power cycle | Legacy Command Sweep | Tested `AB 01`, `AB 02`, `AB 06`, `AB 07`, `55 AA`, `55 AA 01 01`, `AE AE 55 AA`, and ASCII `AT` after `FD`; no ACK or stream change. | ✅ Neutral |
| **R39** | Continuity | Dual-rail power cycle | Full `AB CD` Frame Sweep | Sent checksum-valid 10-byte button and force-mode frames after `FD`; all returned to unchanged `AB CD 01 19 00 00 7F 00 00 99`. | ✅ Neutral |
| **R40** | Continuity | Dual-rail power cycle | `A5 01` Button-ID Sweep | Tested button IDs `00`-`0F` with `(0x01 + id) & 0xFF` checksum; no ACK, mode change, or stream disruption. | ✅ Neutral |
| **R41** | Continuity | Dual-rail power cycle | `A5 02` Direct-Range Sweep | Tested confirmed and candidate range bytes (`0D`, `17`, `0E`, `1A`, `1C`, `19`, `16`, `13`, `0B`, `1B`, `1D`, `1E`); no change. | ✅ Neutral |
| **R42** | Continuity | Pad 1 (Soft) | Host-Driven NULL Gateway | Sequential PAD1 reset plus 8-64 NULL bursts did not reproduce State 41; normal `01 19` telemetry resumed. Host-side gap is likely too large for this path. | ✅ Neutral |
| **R43** | Continuity | Dual-rail power cycle | External Port Marker Test | External/opto UART emitted `AB ED`, not `AB FD`, so earlier EXT tests waiting for `FD` timed out. | ✅ Discovery |
| **R44** | Continuity | Dual-rail power cycle | External `ED` Injection | Retested EXT using `ED` trigger with legacy/A5/sync candidates; injection worked but telemetry stayed unchanged. One non-reproducible `FD` marker was observed. | ✅ Neutral |
| **R45** | Continuity | Dual-rail power cycle | External Marker Confirmation | No-injection observation pass confirmed external boot marker `AB ED` on 8/8 cycles at ~1.11s after power-on. | ✅ Discovery |
| **R46** | 200mV DC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 200mV frames use range byte `17`; internal boot marker remained `AB FD`. | ✅ Success |
| **R47** | 200mV DC | Dual-rail power cycle | Internal 200mV Command Probes | Tested `A5`, A5 button/direct-mode variants, legacy `AB` commands, and full frames after internal `FD`; telemetry stayed in `01 17`. | ✅ Neutral |
| **R48** | 200mV DC | Dual-rail power cycle | External Marker Observation | External/opto UART emitted `AB FD` in 200mV mode, not `AB ED`; marker appears mode-dependent. | ✅ Discovery |
| **R49** | 200mV DC | Dual-rail power cycle | External 200mV Command Probes | Retested external A5/legacy/direct-mode candidates using `ED FD` triggers; matched `FD` and telemetry stayed in `01 17`. | ✅ Neutral |
| **R50** | 2000mV DC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 2000mV frames use previously-unmapped range byte `07`; internal boot marker was `AB FD`. | ✅ Discovery |
| **R51** | 2000mV DC | Dual-rail power cycle | Internal 2000mV Command Probes | Tested A5, A5 button/direct-mode variants, legacy `AB`, and full-frame `01 07`; telemetry stayed in `01 07`. | ✅ Neutral |
| **R52** | 2000mV DC | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` during no-injection observation in 2000mV mode. | ✅ Success |
| **R53** | 2000mV DC | Dual-rail power cycle | External 2000mV Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched both `FD` and occasional `ED`, telemetry stayed in `01 07`. | ✅ Neutral |
| **R54** | 20V DC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 20V frames use range byte `0D`; internal marker was `AB FD`. | ✅ Success |
| **R55** | 20V DC | Dual-rail power cycle | Fast Internal 20V Command Probes | After optimizing firmware to inject before USB logging, tested A5, A5 button/direct-mode, legacy `AB`, and full-frame `01 0D`; telemetry stayed in `01 0D`. | ✅ Neutral |
| **R56** | 20V DC | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` in 20V mode. | ✅ Success |
| **R57** | 20V DC | Dual-rail power cycle | Fast External 20V Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched `FD`, telemetry stayed in `01 0D`. | ✅ Neutral |
| **R58** | 200V DC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 200V frames use range byte `15`; internal marker was `AB FD`. | ✅ Discovery |
| **R59** | 200V DC | Dual-rail power cycle | Fast Internal 200V Command Probes | Tested A5, A5 button/direct-mode, legacy `AB`, and full-frame `01 15`; telemetry stayed in `01 15`. | ✅ Neutral |
| **R60** | 200V DC | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` in 200V mode. | ✅ Success |
| **R61** | 200V DC | Dual-rail power cycle | Fast External 200V Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched `FD`, telemetry stayed in `01 15`. | ✅ Neutral |
| **R62** | 600V DC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 600V frames use range byte `18`; internal marker was `AB FD`. | ✅ Discovery |
| **R63** | 600V DC | Dual-rail power cycle | Fast Internal 600V Command Probes | Tested A5, A5 button/direct-mode, legacy `AB`, and full-frame `01 18`; telemetry stayed in `01 18`. | ✅ Neutral |
| **R64** | 600V DC | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` in 600V mode. | ✅ Success |
| **R65** | 600V DC | Dual-rail power cycle | Fast External 600V Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched `FD`, telemetry stayed in `01 18`. | ✅ Neutral |
| **R66** | 600V AC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 600VAC frames use range byte `11`; internal marker was `AB FD`. | ✅ Discovery |
| **R67** | 600V AC | Dual-rail power cycle | Fast Internal 600VAC Command Probes | Tested A5, A5 button/direct-mode, legacy `AB`, and full-frame `01 11`; telemetry stayed in `01 11`. | ✅ Neutral |
| **R68** | 600V AC | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` in 600VAC mode. | ✅ Success |
| **R69** | 600V AC | Dual-rail power cycle | Fast External 600VAC Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched `FD`, telemetry stayed in `01 11`. | ✅ Neutral |
| **R70** | 200V AC | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal 200VAC frames use range byte `12`; internal marker was `AB FD`. | ✅ Discovery |
| **R71** | 200V AC | Dual-rail power cycle | Fast Internal 200VAC Command Probes | Tested A5, A5 button/direct-mode, legacy `AB`, and full-frame `01 12`; telemetry stayed in `01 12`. | ✅ Neutral |
| **R72** | 200V AC | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` in 200VAC mode. | ✅ Success |
| **R73** | 200V AC | Dual-rail power cycle | Fast External 200VAC Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched `FD`, telemetry stayed in `01 12`. | ✅ Neutral |
| **R74** | Celsius | Dual-rail power cycle | Baseline Marker Observation | Confirmed normal Celsius frames use range byte `16`; internal marker was `AB FD`; open-probe frames repeated `AB CD 01 16 00 00 FF 7F 01 95`. | ✅ Discovery |
| **R75** | Celsius | Dual-rail power cycle | Fast Internal Celsius Command Probes | Tested A5, A5 button/direct-mode, legacy `AB`, force Fahrenheit/20V, and full-frame `01 16`; telemetry stayed in `01 16`. | ✅ Neutral |
| **R76** | Celsius | Dual-rail power cycle | External Marker Observation | External/opto marker was `AB FD` in Celsius mode. | ✅ Success |
| **R77** | Celsius | Dual-rail power cycle | Fast External Celsius Command Probes | Retested external A5/legacy/direct-mode candidates with `ED FD` trigger list; matched `FD`, telemetry stayed in `01 16`. | ✅ Neutral |
| **R78** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Button-Held Marker Observation | Internal and external marker captures matched `AB FD` on 4/4 cycles each; no `41`, `F9`, or `81` appeared. This differs from earlier no-button external Continuity `AB ED`. | ✅ Discovery |
| **R79** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Button-Held FD Command Probes | Tested A5, A5 null/button/direct-mode, NULL preamble, and legacy `AB` on both channels after `FD`; telemetry stayed `01 19`. | ✅ Neutral |
| **R80** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Button-Held Early E0 Probes | Injected A5/null/sync candidates after early `E0`; later `AB FD` still appeared and telemetry returned to `01 19`. | ✅ Neutral |
| **R81** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Button-Held Marker Repeat | Repeated the same physical-button condition; internal and external marker captures again matched `AB FD` on 4/4 cycles each, with no `41`, `F9`, or `81` in the marker window. | ✅ Success |
| **R82** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Button-Held FD Command Probe Repeat | Repeated button-held A5/button/direct-mode, NULL preamble, and legacy `AB` probes on both channels after `FD`; telemetry stayed `01 19`. One external cycle showed early `F0`. | ✅ Neutral |
| **R83** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Passive External Early-Byte Capture | Passive no-injection captures of the same button-held condition showed early external `FF`, `F0`, and `F9` before the normal `E0` -> `AB FD` -> `01 19` sequence. `F9` recurred at ~10ms after power-on. | ✅ Discovery |
| **R84** | Continuity + HOLD/SELECT + Backlight held | Dual-rail power cycle | Passive Combined-Button Capture | Ten passive full power-cycle captures showed internal `AB FD` every time, but external alternated between `AB ED` and `AB FD`; no early `F9` recurred. Normal telemetry stayed `01 19`. | ✅ Discovery |
| **R85** | Device OFF + HOLD/SELECT + Backlight held | Dual-rail power cycle | Passive Off-State Capture | Five clean power restores produced no internal or external UART bytes. The OFF dial/device state appears to gate MCU telemetry completely even with both buttons held. | ✅ Neutral |
| **R86** | Continuity + HOLD/SELECT held | Dual-rail power cycle | F9 Repeatability Attempt (1.5s) | Five cycles at 2400 baud did not reproduce the early external `F9`. Observed early `E0` followed by `AB FD` and normal `01 19`. | ✅ Neutral |
| **R87** | Continuity + HOLD/SELECT held | Dual-rail power cycle | F9 Repeatability Attempt (9k6) | One cycle at 9600 baud showed junk data but no clear `F9` signature. | ✅ Neutral |
| **R88** | Continuity + HOLD/SELECT held | Dual-rail power cycle | F9 Repeatability Attempt (5s) | Increased discharge delay to 5s to ensure clean boot. Still did not reproduce early `F9`. | ✅ Neutral |
| **R89** | Continuity + HOLD/SELECT + Backlight held | Dual-rail power cycle | Combined F9 Repeatability (5s) | Holding both buttons with 5s discharge did not reproduce `F9`. | ✅ Neutral |
| **R90** | Continuity + HOLD/SELECT held | Pad 1 (Soft Reset) | Soft-Reset Boot Window Test | Pulsing Pad 1 while power was ON skipped the early boot markers entirely; normal telemetry resumed immediately. | ✅ Discovery |
| **R91** | Continuity + HOLD/SELECT held | Dual-rail power cycle | Autonomous Multi-Baud Sweep | Exhaustive sweep of 810 payload permutations (0xA5 + 00-FF, legacy syncs, full frames) injected immediately after `FD` marker at 2400, 9600, and 115200 baud. All attempts were ignored or safely dropped. | ✅ Neutral (Conclusive) |

---

## 🔍 Analytical Conclusions (May 24, 2026)

### 1. The Gateway (State 41 and F9)
We have identified an explicit **"Awaiting Communication"** state (Protocol ID `41`) and additional markers like `F9` and `81` which occur during the boot sequence or when the physical HOLD/SELECT button is held. The `F9` marker seen in R83 appears to be extremely transient and potentially dependent on very specific capacitor discharge states; R86-R89 were unable to repeat it reliably.

### 2. Physical Verification & Mandatory Buttons
Experiment R27 confirmed that the MCU ignores all UART injection unless the physical HOLD/SELECT button is held during the reset. This confirms a hardware strapping requirement for entering diagnostic or calibration modes.

### 3. Reset Strategy Shift (Soft vs Hard)
Experiment R32 and R90 revealed that **Soft Reset (Pad 1)** is unstable for diagnostic entry. While it resets the measurement loop, it often skips the bootloader listener window entirely. **Hard-Power Reset (Dual-Rail MOSFETs)** with a 5-second discharge delay is the only reliable way to ensure the MCU enters its true boot state.

### 4. Bootloader Timing Delay
Through R33, we discovered that the MCU's bootloader takes approximately **1.2 seconds** after a Hard Power-ON to initialize and emit the `AB FD` marker when the HOLD/SELECT button is held.

### 5. Serial-Controlled Rig Firmware
The Pico rig firmware has been updated to include `RESET_MARKER`, allowing the rig to pulse Pad 1 or Pad 2 and immediately watch for markers without a full power cycle. The `CYCLE_MARKER` command now defaults to a **5-second** power-off delay to ensure "True Zero" resets.

### 6. Mode-Dependent Boot Markers
R43/R45 first showed the external/opto UART emitted `AB ED` in Continuity while the internal UART emitted `AB FD`. R48/R49 corrected this model: in 200mV mode, the external/opto UART emits `AB FD` too.
*   **Internal UART:** `AB FD` in tested modes.
*   **External/opto UART, Continuity, no held button:** `AB ED`.
*   **External/opto UART, Continuity, HOLD/SELECT held:** `AB FD`, with occasional early `FF`/`F0`/`F9` before `E0`.
*   **External/opto UART, Continuity, HOLD/SELECT + Backlight held:** mixed `AB ED`/`AB FD`; no early `F9` in R84.
*   **External/opto UART, 200mV:** `AB FD`.
*   **External/opto UART, 2000mV:** `AB FD` in observation, with occasional `ED` during command-probe cycles.
*   **External/opto UART, 20V:** `AB FD`.
*   **External/opto UART, 200V:** `AB FD`.
*   **External/opto UART, 600V:** `AB FD`.
*   **External/opto UART, 600VAC:** `AB FD`.
*   **External/opto UART, 200VAC:** `AB FD`.
*   **External/opto UART, Celsius:** `AB FD`.
Future external-port tests should trigger on both `ED` and `FD` unless the target mode has already been characterized.

### 7. Marker Response Timing Correction
Before R54, the firmware logged the marker byte over USB before sending the response bytes. The firmware now writes the response immediately after reading a matched marker, then logs the event.

### 8. Power Sequencing & Rig Hardware
A "Clean" reset requires an **Inverted Dual-Rail cut**:
*   **3.3V (GP16):** Active HIGH (1=ON)
*   **GND (GP17):** Active LOW (0=ON)
*   **Wait Time:** **5.0s** is now recommended (updated from 1.5s) to ensure full capacitor discharge.
*   The rig uses the **RP2040 (Pico)** with serial-controlled firmware.

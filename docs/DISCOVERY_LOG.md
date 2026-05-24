# UT33C+ UART Discovery Log
Chronological record of technical findings and protocol anomalies.

---

## May 24, 2026: Automated HIL Discovery

### 1. The "Boot/Status" Signature
*   **Discovery:** Immediately after a power-cycle or Pad 2 Reset, the meter transmits a series of frames with a different Protocol ID.
*   **Normal ID:** `01`
*   **Boot ID:** `81`
*   **Duration:** Lasts for ~500ms before switching to `01`.
*   **Significance:** Indicates a separate initialization firmware path. This is the primary window for RX "unlock" commands.

### 2. Mode Byte Bit-Flipping (`0D` vs `8D`)
*   **Anomaly:** During the `AB 00 - AB 0F` fuzzer range in 20V mode, the mode byte flipped from `0D` to `8D`.
*   **Analysis:** The high bit (`0x80`) is being used as a status flag. Since `0D` is 20V mode, `8D` might indicate "Mode Locked" or "Diagnostic Mode Active."

### 3. RX Physical Verification (Reflection Artifacts)
*   **Finding:** When injecting `55 AA` (binary `01010101 10101010`), the TX stream on the external port showed literal `55 AA` artifacts.
*   **Conclusion:** This **PROVES** the fuzzer's RX line is physically reaching the multimeter's MCU. The data is being buffered and echoed, confirming the hardware link is valid.

### 4. Power Rail Sequencing Success
*   **Discovery:** Standard high-side power cutting was insufficient. 
*   **Verification:** A successful cycle requires an **inverted dual-rail cut**:
    *   `GP16` (3.3V) -> LOW
    *   `GP17` (GND) -> HIGH
    *   **Discharge Time:** **5.0 seconds** recommended (updated from 1.5s) to ensure "True Zero" resets of the MCU and ADC.

### 5. ADC Saturation State (`7F FF`)
*   **Observation:** During specific reset windows, the ADC count reports `7F FF` instead of the expected `00 00` or floating values.
*   **Analysis:** This indicates the ADC is in "Saturation" or "Not Ready" state while the MCU performs its own internal self-test.

### 7. Chipset Identification: SDIC SD7501
*   **Discovery:** Comparative protocol research identifies the UT33C+ IC as likely an **SD7501** (or derivative from Jinghua Microelectronics).
*   **Key Evidence:** Native 10-byte protocol @ 2400 baud and the specific `AB CD` header found across the "plus" series.

### 8. The "Ready" Signal (State 41 / ASCII 'A')
*   **Discovery:** In SDIC/Jinghua bootloaders, responding with `0x41` (ASCII 'A') indicates the MCU has successfully synchronized with a serial handshake (the NULL burst) and is awaiting a **Command Prefix**.
*   **Handshake Key:** Standard command prefix for this chipset is **`0xA5`**.

### 9. Hardware Strapping (Button Requirement)
*   **Finding:** Diagnostic mode entry is **hardware-strapped**. 
*   **Verification:** Experiment R27 confirmed that the MCU ignores all UART activity unless the physical HOLD/SELECT button is held during the reset window.
*   **Timing:** The bootloader listener window opens approximately **1.2 seconds** after a Hard Power-ON, signaled by an `AB FD` marker.

### 10. Soft vs Hard Reset Limitations
*   **Discovery:** **Soft Reset (Pad 1)** is unreliable for entering State 41 when the HOLD/SELECT button is held. R90 confirmed that pulsing Pad 1 while power is ON skips the bootloader listener window entirely.
*   **Solution:** **Hard Power-ON Reset (via dual-rail MOSFETs)** with 5s discharge provides the most consistent entry point for the diagnostic gateway.

### 11. Timing Criticality of Command Injection
*   **Finding:** The "Diagnostic Door" is only open for a few tens of milliseconds after the `AB FD` marker. 
*   **Requirement:** Commands like `0xA5` must be injected with high precision immediately upon detecting the marker, making the use of hardware interrupts on the Pico essential for the next phase.

### 12. Mode-Dependent Boot Markers
*   **Discovery:** The external/opto listener marker is mode-dependent.
*   **Internal:** `AB FD` in tested modes.
*   **External Continuity, no held button:** `AB ED`.
*   **External Continuity, HOLD/SELECT held:** `AB FD`, with occasional early `FF`/`F0`/`F9` before `E0`.
*   **External Continuity, HOLD/SELECT + Backlight held:** mixed `AB ED`/`AB FD`; no early `F9` in R84.
*   **External 200mV:** `AB FD`.
*   **External 2000mV:** `AB FD` during no-injection observation, with occasional `ED` during command-probe cycles.
*   **External 20V:** `AB FD`.
*   **External 200V:** `AB FD`.
*   **External 600V:** `AB FD`.
*   **External 600VAC:** `AB FD`.
*   **External 200VAC:** `AB FD`.
*   **External Celsius:** `AB FD`.
*   **Verification:** R45 observed `AB ED` on the external channel in 8/8 Continuity no-injection cycles. R78 and R81 observed `AB FD` on the external channel in repeated HOLD/SELECT-held Continuity cycles, and R83 later observed early `F9` before `E0` during passive HOLD/SELECT-held capture. R84 observed mixed `AB ED`/`AB FD` externally when HOLD/SELECT and Backlight were held together. R48/R49 then observed `AB FD` on the external channel in 200mV mode. R52/R53 observed `FD` plus occasional `ED` in 2000mV mode. R56/R57 observed `FD` in 20V mode. R60/R61 observed `FD` in 200V mode. R64/R65 observed `FD` in 600V mode. R68/R69 observed `FD` in 600VAC mode. R72/R73 observed `FD` in 200VAC mode. R76/R77 observed `FD` in Celsius mode.
*   **Impact:** External-port tests must trigger on both `ED` and `FD` unless the target dial mode and button-held state have already been characterized.

### 13. 2000mV Range Byte
*   **Discovery:** The 2000mV dial range reports normal frames as `AB CD 01 07 ...`.
*   **Impact:** Range byte `07` should be treated as 2000mV DC. Scaling still needs fixture validation with a known input voltage.

### 14. 200V Range Byte
*   **Discovery:** The 200V dial range reports normal frames as `AB CD 01 15 ...`.
*   **Impact:** Range byte `15` should be treated as 200V DC. Scaling still needs fixture validation with a known input voltage.

### 15. 600V Range Byte
*   **Discovery:** The 600V dial range reports normal frames as `AB CD 01 18 ...`.
*   **Impact:** Range byte `18` should be treated as 600V DC. Scaling still needs fixture validation with a known input voltage.

### 16. 600VAC Range Byte
*   **Discovery:** The 600VAC dial range reports normal frames as `AB CD 01 11 ...`.
*   **Impact:** Range byte `11` should be treated as 600V AC. Scaling still needs fixture validation with a known AC source.

### 17. 200VAC Range Byte
*   **Discovery:** The 200VAC dial range reports normal frames as `AB CD 01 12 ...`.
*   **Impact:** Range byte `12` should be treated as 200V AC. Scaling still needs fixture validation with a known AC source.

### 18. Celsius Range Byte
*   **Discovery:** The Celsius dial range reports normal frames as `AB CD 01 16 ...`.
*   **Observation:** With the current open/unconnected temperature input, frames repeatedly included `00 00 FF 7F 01 95`.
*   **Impact:** Range byte `16` is confirmed as Celsius. Temperature scaling remains `count * 0.1 deg C`, but the open-input pattern needs thermocouple fixture validation.

### 19. HOLD/SELECT-Held Continuity Marker
*   **Discovery:** Holding the HOLD/SELECT button in Continuity changed the external/opto boot marker from the earlier no-button `AB ED` pattern to `AB FD`.
*   **Observation:** R78 saw `AB FD` on 4/4 internal and 4/4 external cycles; R79/R80 command probes after `FD` and early `E0` remained neutral.
*   **Impact:** The boot marker is not only mode-dependent; it is also affected by physical button state. Future marker capture should record dial mode and held-button condition together.

### 20. HOLD/SELECT-Held Early External F9
*   **Discovery:** Passive HOLD/SELECT-held Continuity capture reproduced an early external `F9` byte before the normal `E0` and `AB FD` sequence.
*   **Observation:** R83 saw passive external starts of `E0`, `F0`, `FF E0`, and `F9 E0`.
*   **Update (R86-R89):** Repeated attempts with 1.5s and 5.0s discharge delays failed to reproduce the early `F9`. This marker is extremely transient and likely highly dependent on power-rail decay states.

### 21. HOLD/SELECT + Backlight Combined Button State
*   **Discovery:** Holding HOLD/SELECT and Backlight together in Continuity did not reproduce the early `F9`; instead, the external/opto boot marker became mixed.
*   **Observation:** R84 used ten passive full dual-rail power cycles. Internal marker was `AB FD` on every cycle. External marker was `AB ED` on attempts 1, 5, and 7, and `AB FD` on the remaining seven attempts. Normal telemetry stayed `AB CD 01 19 00 00 7F 00 00 99`.
*   **Impact:** Backlight changes the button-held boot path enough to partially restore the no-button Continuity external `ED` marker. This looks less promising than HOLD/SELECT-only for the early `F9` route.

### 22. Device OFF + Both Buttons
*   **Discovery:** With the device/dial OFF and both HOLD/SELECT and Backlight held, the meter produced no UART output after full rail power restore.
*   **Observation:** R85 ran five passive 5s captures after 1.5s dual-rail-off discharge; both internal and external byte counts were zero on all attempts.
*   **Impact:** OFF state is not a useful diagnostic-entry route through the current UART pads. Tests should return to an active dial mode, preferably Continuity, before probing early markers.

### 23. Marker Injection Latency Fix
*   **Discovery:** The first command firmware logged matched marker bytes over USB before transmitting the response payload.
*   **Fix:** Before R54, firmware was changed to transmit the response immediately on marker match and log afterward.
*   **Impact:** R54+ tests use the fastest current Arduino-core path.

### 24. Firmware Feature: RESET_MARKER
*   **Discovery:** Handshake attempts often failed due to the host-side latency of the USB serial link when combining RESET and MONITOR commands.
*   **Implementation:** Added `RESET_MARKER` to the Pico firmware. This command pulses a reset pin (Pad 1 or Pad 2) and immediately starts the marker-response listener on the Pico, eliminating USB round-trip latency during the critical boot window.

---

## Fuzzer Experiment Matrix (Updated May 24, 2026)

| Run ID | Meter Mode | Reset Trigger | Strategy | Discovery / Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R01-R11** | Various | Pad 1/2 | Basic Fuzzing | Found IDs `81` and `41`. Confirmed 2400 baud native filtering. | Complete |
| **R12-R19** | Continuity | Pad 1 (Soft) | Adv. Timing | Confirmed ID `41` is transient; NULL blasts do not sustain it. | Complete |
| **R20** | Continuity | Pad 1 (Soft) | Stabilization | Gateway is timing-critical and ignores ASCII strings. | Success |
| **R25** | Continuity | Pad 1 (Soft) | Hold/Select & Reset | User held the HOLD/SELECT button. Found new markers: `F9` and `81`. | Success |
| **R27** | Continuity | Pad 1 (Soft) | Auto Discovery | Confirmed **Physical Button is Mandatory** for gateway entry. | Success |
| **R30-R31** | Continuity | Pad 2 (Hard) | Hard-Power | Identified early boot markers (`E0`, `AB FD`) after full power cycle. | Success |
| **R33** | Continuity | Pad 2 (Hard) | Hard-Power | Discovered `AB FD` marker consistently appears at **1.2s offset**. | Success |
| **R34-R42** | Continuity | Hard/Soft Reset | Command Sweeps | Tested A5, legacy AB, full frames, direct range, and host-driven NULL gateway paths; no ACK or mode transition. | Neutral |
| **R43-R45** | Continuity, no held button | Pad 2 (Hard) | External Marker Analysis | Confirmed external marker is `AB ED` in no-button Continuity while internal remains `AB FD`. | Success |
| **R46-R49** | 200mV DC | Pad 2 (Hard) | 200mV Marker + Command Tests | Confirmed `01 17` telemetry and found external marker changes to `AB FD` in 200mV mode. Command probes remained neutral. | Success |
| **R50-R53** | 2000mV DC | Pad 2 (Hard) | 2000mV Marker + Command Tests | Discovered range byte `07`; command probes remained neutral. External marker mostly `FD`, sometimes `ED` during probes. | Success |
| **R54-R57** | 20V DC | Pad 2 (Hard) | Fast 20V Marker + Command Tests | Confirmed `01 0D` telemetry and `AB FD` markers on both channels after latency fix. Command probes remained neutral. | Success |
| **R58-R61** | 200V DC | Pad 2 (Hard) | Fast 200V Marker + Command Tests | Discovered range byte `15`; `AB FD` markers on both channels. Command probes remained neutral. | Success |
| **R62-R65** | 600V DC | Pad 2 (Hard) | Fast 600V Marker + Command Tests | Discovered range byte `18`; `AB FD` markers on both channels. Command probes remained neutral. | Success |
| **R66-R69** | 600V AC | Pad 2 (Hard) | Fast 600VAC Marker + Command Tests | Discovered range byte `11`; `AB FD` markers on both channels. Command probes remained neutral. | Success |
| **R70-R73** | 200V AC | Pad 2 (Hard) | Fast 200VAC Marker + Command Tests | Discovered range byte `12`; `AB FD` markers on both channels. Command probes remained neutral. | Success |
| **R74-R77** | Celsius | Pad 2 (Hard) | Fast Celsius Marker + Command Tests | Confirmed `01 16` telemetry and `AB FD` markers on both channels. Command probes remained neutral. | Success |
| **R78-R80** | Continuity + HOLD/SELECT held | Pad 2 (Hard) | Button-Held Marker + Command Tests | Found button-held external Continuity uses `AB FD` instead of earlier no-button `AB ED`; command probes remained neutral. | Discovery |
| **R81-R83** | Continuity + HOLD/SELECT held | Pad 2 (Hard) | Button-Held Repeat + Passive Early Capture | Repeated the same physical-button condition; passive early capture saw `FF`, `F0`, and `F9` before `E0`. | Discovery |
| **R84** | Continuity + HOLD/SELECT + Backlight held | Pad 2 (Hard) | Passive Combined-Button Capture | External marker mixed `AB ED`/`AB FD`; early `F9` did not recur. | Discovery |
| **R85** | Device OFF + HOLD/SELECT + Backlight held | Pad 2 (Hard) | Passive Off-State Capture | No internal or external UART bytes on five clean power restores. | Neutral |
| **R86-R89** | Continuity + HOLD/SELECT held | Pad 2 (Hard) | F9 Repeatability Tests | 1.5s and 5.0s discharge attempts failed to reproduce early `F9` on external UART. | Neutral |
| **R90** | Continuity + HOLD/SELECT held | Pad 1 (Soft) | Soft-Reset Boot Window Test | Pulsing Pad 1 while power was ON skipped the early boot markers entirely. | Discovery |
| **R91** | Continuity + HOLD/SELECT held | Pad 2 (Hard) | Autonomous Multi-Baud Sweep | Exhaustive sweep of 810 payload permutations (0xA5 + 00-FF, legacy syncs, full frames) injected immediately after `FD` marker at 2400, 9600, and 115200 baud. All attempts ignored. | Neutral (Conclusive) |

### Future Targets (Remaining to be tried):
1.  **EEPROM Corruption via WDT:** Hammering Pad 1 Soft Reset while blasting junk data to intentionally corrupt the RAM/EEPROM bounds check.
2.  **Logic Analyzer Trace:** Capturing the physical factory calibration process with a logic analyzer (if possible) to find the true multi-byte OEM authorization key.

**Conclusion of Active Fuzzing:** The State 41 gateway exists and the physical wiring is sound, but the diagnostic mode is strictly gated behind an unknown, likely multi-byte authorization key. Standard single-byte fuzzing is insufficient. Active reverse engineering of the bootloader handshake is concluded.

---

## Hardware Mapping (YD-RP2040)
| Function | Pin | Logic |
| :--- | :--- | :--- |
| Internal TX | GP1 | 2400 Baud |
| Internal RX | GP0 | 2400 Baud (Command Injection) |
| External TX | GP5 | 2400 Baud (Noisy) |
| External RX | GP4 | 2400 Baud |
| Power 3.3V | GP16 | Active HIGH (1=ON) |
| Power GND | GP17 | Active LOW (0=ON) |
| Soft Reset | GP14 | Active LOW (Pad 1) |
| Hard Reset | GP15 | Active LOW (Pad 2) |

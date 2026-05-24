# UT33C+ UART Discovery Log
Chronological record of technical findings and protocol anomalies.

---

## 📅 May 24, 2026: Automated HIL Discovery

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
    *   **Discharge Time:** 1.5 seconds minimum to clear ADC registers.

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
*   **Verification:** Experiment R27 confirmed that the MCU ignores all UART activity unless a physical button (SELECT or HOLD) is held during the reset window.
*   **Timing:** The bootloader listener window opens approximately **1.2 seconds** after a Hard Power-ON, signaled by an `AB FD` marker.

### 10. Soft vs Hard Reset Limitations
*   **Discovery:** **Soft Reset (Pad 1)** is unreliable for entering State 41 when physical buttons are held. The MCU often "short-circuits" the listener window and proceeds to standard measurement.
*   **Solution:** **Hard Power-ON Reset (via dual-rail MOSFETs)** provides the most consistent entry point for the diagnostic gateway.

### 11. Timing Criticality of Command Injection
*   **Finding:** The "Diagnostic Door" is only open for a few tens of milliseconds after the `AB FD` marker. 
*   **Requirement:** Commands like `0xA5` must be injected with high precision immediately upon detecting the marker, making the use of hardware interrupts on the Pico essential for the next phase.

---

## 📊 Fuzzer Experiment Matrix (Updated May 24, 2026)

| Run ID | Meter Mode | Reset Trigger | Strategy | Discovery / Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R01-R11** | Various | Pad 1/2 | Basic Fuzzing | Found IDs `81` and `41`. Confirmed 2400 baud native filtering. | ✅ Complete |
| **R12-R19** | Continuity | Pad 1 (Soft) | Adv. Timing | Confirmed ID `41` is transient; NULL blasts do not sustain it. | ✅ Complete |
| **R20** | Continuity | Pad 1 (Soft) | Stabilization | Gateway is timing-critical and ignores ASCII strings. | ✅ Success |
| **R25** | Continuity | Pad 1 (Soft) | Hold & Reset | User held SELECT. Found new markers: `F9` and `81`. | ✅ Success |
| **R27** | Continuity | Pad 1 (Soft) | Auto Discovery | Confirmed **Physical Button is Mandatory** for gateway entry. | ✅ Success |
| **R30-R31** | Continuity | Pad 2 (Hard) | Hard-Power | Identified early boot markers (`E0`, `AB FD`) after full power cycle. | ✅ Success |
| **R33** | Continuity | Pad 2 (Hard) | Hard-Power | Discovered `AB FD` marker consistently appears at **1.2s offset**. | ✅ Success |
| **R34** | Continuity | Pad 2 (Hard) | Precise Resp. | *Awaiting Run - Target: 0xA5 command injection at 1.2s* | 🕒 Active |

### 🚀 Future Targets (Remaining to be tried):
1.  **Multi-Baud Handshake:** Testing Pad 1 Reset while injecting at 9600 or 115200 baud.
2.  **Long Burst (WDT):** Sending continuous `00` or `FF` for 5+ seconds to trigger a Watchdog Timeout or Buffer Overflow.
3.  **Power-On Glitch:** Rapid dual-rail power cycling (<100ms) to bypass initialization checksums.

---

## 🛠 Hardware Mapping (YD-RP2040)
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

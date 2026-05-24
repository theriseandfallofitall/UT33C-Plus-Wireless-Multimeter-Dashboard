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

### 6. Transition to "Burst Mode" Fuzzing
*   **Strategy Shift:** Single and 2-byte fuzzing confirmed the physical link but failed to trigger a diagnostic mode.
*   **New Approach:** Implementing a library of multi-byte sequences ("SET", "FACTORY", "UNI-T") to blast during the Soft Reset (Pad 1) window.
*   **Goal:** Trigger complex state machine transitions in the bootloader that require multi-character handshakes.

---

## 📊 Fuzzer Experiment Matrix

| Run ID | Meter Mode | Reset Trigger | Strategy | Duration | Result / Discovery | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R01** | 20V DC | Pad 2 (Hard) | Deep (AB 00-FF) | 7m | Found `81` ID & `8D` flag artifact | ✅ Complete |
| **R02** | 10A DC | Pad 2 (Hard) | Deep (AB 00-FF) | 7m | Confirmed dynamic `81 0B` signature | ✅ Complete |
| **R03** | Continuity | Pad 2 (Hard) | Deep (AB 00-FF) | 7m | Long `81` persistence, noise reflection | ✅ Complete |
| **R04** | Continuity | Pad 1 (Soft) | Deep (AB 00-FF) | 7m | Soft Reset window confirmed valid | ✅ Complete |
| **R05** | Continuity | Pad 1 (Soft) | Burst Library | 2m | Discovered **Protocol ID 41** after NULL burst. FACTORY burst triggered immediate output before header. | ✅ Complete |
| **R06** | Continuity | Pad 1 (Soft) | Null Hold (2s) | 3m | **Confirmed ID 41 stability.** Continuous NULL hold pinned the MCU in ID 41 state. ID 41 also appeared after UNI-T and RESET bursts. | ✅ Complete |
| **R08** | Continuity | Pad 1 (Soft) | State 41 Deep Fuzz | 7m | **State 41 verified as stable.** All 256 single-byte commands maintained ID 41 without triggering a secondary state transition. | ✅ Complete |
| **R09** | Continuity | Pad 1 (Soft) | State 41 Burst | 2m | **No Data Dump triggered.** Bursts ('READ', 'INFO', etc.) caused reflections and transient '41' or '81' states, but meter returned to measurement loop. | ✅ Complete |
| **R10** | Continuity | Pad 1 (Soft) | Multi-Baud (9600) | 2m | **Injection Ignored.** 9600 baud bursts did not trigger any state changes. Meter maintained standard `81 -> 01` boot transition. | ✅ Complete |
| **R11** | Continuity | Pad 1 (Soft) | Multi-Baud (115200) | 2m | **Injection Ignored.** 115k baud high-speed bursts did not trigger diagnostic shifts. MCU appears to filter non-2400 baud data during boot. | ✅ Complete |
| **R12** | Continuity | Pad 1 (Soft) | Long NULL Blast (10s) | 2m | *Awaiting Run - Hunting for Watchdog/Buffer overflow* | 🕒 Pending |
| **R07** | 10A DC | Pad 1 (Soft) | Burst Library | 2m | *Awaiting Run* | 🕒 Pending |

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

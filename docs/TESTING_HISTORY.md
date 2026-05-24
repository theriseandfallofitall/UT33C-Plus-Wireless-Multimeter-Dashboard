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
| **R25** | Continuity | Pad 1 (Soft) | Hold & Reset | User held SELECT button. Discovered new markers (`AB CD F9` and `AB CD 81`). | ✅ Success |
| **R26** | Continuity | Pad 1 (Soft) | Real-time Handshake | Monitored for non-standard bytes to send 0xA5. Failed. | ✅ Neutral |
| **R27** | Continuity | Pad 1 (Soft) | Auto Discovery | Swept parameters without physical button. Confirmed physical interaction is mandatory for diagnostic entry. | ✅ Success |
| **R28** | Continuity | Pad 1 (Soft) | Targeted Physical | Sent 16x NULL + 0xA5 while holding SELECT. No ACK received. | ✅ Neutral |
| **R29** | Continuity | Pad 1 (Soft) | Gateway Probe | Very short 10ms reset pulse, sliding delay before NULLs. Gateway not triggered. | ✅ Neutral |
| **R30** | Continuity | Pad 2 (Hard) | Hard-Power Glitch | Power cycled the MCU. Detected `E0` and `AB FD` markers confirming early boot window access. | ✅ Success |
| **R31** | Continuity | Pad 2 (Hard) | Pre-Power Sync | Blasted `0x55 0xAA` before power-on. Still received `FE` and `AB FD`. | ✅ Success |
| **R32** | Continuity | Pad 1 (Soft) | EEPROM Read | Sent formatted READ command (`0xA5 0x00 [ADDR] [CS]`) after boot marker. | ⏳ Pending |

---

## 🔍 Analytical Conclusions (May 24, 2026)

### 1. The Gateway (State 41 and F9)
We have identified an explicit **"Awaiting Communication"** state (Protocol ID `41`) and additional markers like `F9` and `81` which occur during the boot sequence or when physical buttons are held. The states are **extremely transient**.

### 2. Physical Verification & Mandatory Buttons
Experiment R27 confirmed that the MCU ignores all UART injection unless a physical button (like SELECT or HOLD) is held during the reset. This confirms a hardware strapping requirement for entering diagnostic or calibration modes.

### 3. Early Boot Markers
Through Hard-Power Glitch experiments (R30, R31), we identified that the MCU emits markers like `E0` and `AB FD` immediately after power-on. We are currently trying to inject sync bytes or commands right at this boot phase.

### 4. Power Sequencing & Rig Hardware
A "Clean" reset requires an **Inverted Dual-Rail cut**:
*   **3.3V (GP16):** Active HIGH (1=ON)
*   **GND (GP17):** Active LOW (0=ON)
*   **Wait Time:** 1.5s is required to clear ADC saturation registers (`7F FF`).
*   The rig has been updated to use the **RP2350 (Pico 2)** to leverage higher precision timers for the stabilization window.

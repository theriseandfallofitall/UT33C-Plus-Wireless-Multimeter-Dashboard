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
| **R20** | Continuity | Pad 1 (Soft) | Stabilization | Tested variable post-trigger delays (10-200ms). Gateway is timing-critical. | ⏳ Pending |

---

## 🔍 Analytical Conclusions (May 24, 2026)

### 1. The Gateway (State 41)
We have identified an explicit **"Awaiting Communication"** state (Protocol ID `41`). This state is triggered by RX activity (specifically NULL bursts) during the Soft Reset window. However, the state is **extremely transient**, often lasting only 10-20ms before the MCU times out and resumes normal measurement.

### 2. Physical Verification
We have confirmed via crosstalk/reflection on the External Port that every command injected by the Pico **physically reaches** the meter's MCU. We are not fighting a wiring issue; we are fighting a firmware "password" or "handshake" requirement that must be sent within a precise micro-window.

### 3. Command Acceptance
Attempts to send ASCII commands (`FACTORY`, `HELP`, `READ`) have so far been ignored. This suggests:
*   The command must be sent *exactly* after the 8th NULL with sub-millisecond precision.
*   The command might require a specific binary prefix or a checksum that we haven't mapped.
*   State 41 might be an error state rather than a shell, though its appearance after NULL bursts strongly suggests a handshake.

### 4. Power Sequencing & Rig Hardware
A "Clean" reset requires an **Inverted Dual-Rail cut**:
*   **3.3V (GP16):** Active HIGH (1=ON)
*   **GND (GP17):** Active LOW (0=ON)
*   **Wait Time:** 1.5s is required to clear ADC saturation registers (`7F FF`).
*   The rig has been updated to use the **RP2350 (Pico 2)** to leverage higher precision timers for the stabilization window.

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

---

## 🔍 Analytical Conclusions (May 24, 2026)

### 1. The Gateway (State 41)
We have identified an explicit **"Awaiting Communication"** state (Protocol ID `41`). This state is triggered by RX activity (specifically NULL bursts) during the Soft Reset window. The meter acknowledge the link but remains in a "Wait" loop.

### 2. Physical Verification
We have confirmed via crosstalk/reflection on the External Port that every command injected by the Pico **physically reaches** the meter's MCU. We are not fighting a wiring issue; we are fighting a firmware "password" or "handshake" requirement.

### 3. Baud Rate Native Filtering
The meter appears to have a hardware-level or early bootloader-level filter that rejects anything other than **2400 baud**. Attempts at 9600 and 115200 were gracefully ignored without crashing or glitching the measurement loop.

### 4. Power Sequencing Requirements
A "Clean" reset requires an **Inverted Dual-Rail cut**:
*   **3.3V (GP16):** Active HIGH (1=ON)
*   **GND (GP17):** Active LOW (0=ON)
*   **Wait Time:** 1.5s is required to clear ADC saturation registers (`7F FF`).

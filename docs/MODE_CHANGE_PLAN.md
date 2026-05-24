# UT33C+ Mode Change Strategy (SD7501 Protocol)

This document outlines the tactical plan for remotely switching multimeter modes via the internal UART port, based on the identification of the **SD7501** chipset.

## 🎯 Objective
Transition the meter from its physical dial state (e.g., Continuity) to a software-controlled state (e.g., 20V DC) using the discovered **State 41** gateway.

---

## 🛠 Handshake Protocol
Research indicates that the SD7501 follows a strict "Trigger-Acknowledge-Command" sequence:

1.  **Trigger:** Pulse Pad 1 (Soft Reset) and send 8x `0x00` (NULL) bytes @ 2400 baud.
2.  **Acknowledge:** Wait for the meter to respond with Protocol ID **`41`** (ASCII 'A').
3.  **Unlock:** Immediately send the **Binary Key `0xA5`**. This is the standard SDIC command prefix.
4.  **Confirm:** Wait for a response (Likely `0x06` ACK or a unique `AB CD 42...` frame).

---

## 🚀 Mode Change Command Set
Once the gateway is "Unlocked" (Step 3), we will test the following command structures:

### Phase 1: Virtual Button Press (Safest)
Most SDIC chips allow simulating the **SELECT** or **RANGE** buttons via UART.
- **Command:** `0xA5 0x01 [Button_ID] [CS]`
- **Button IDs to test:** `0x01` (Select), `0x02` (Range), `0x04` (Hold).

### Phase 2: Direct Mode Injection
Forcing the "Mode Byte" (Byte 3 in the telemetry frame) to a new value.
- **Command:** `0xA5 0x02 [New_Mode] [CS]`
- **Target Modes:** `0x0D` (20V), `0x19` (Continuity).

### Phase 3: EEPROM Write (Advanced)
If the above fail, we may need to write directly to the temporary mode register in internal RAM/EEPROM.
- **Command:** `0xA5 0x10 [Address] [Value] [CS]`

---

## 📊 Experiment Roadmap (R21+)

| ID | Title | Logic | Target Outcome |
| :--- | :--- | :--- | :--- |
| **R21** | The A5 Unlock | NULL -> ID 41 -> Send `0xA5` | Receive ACK (`0x06`) |
| **R22** | Button Sim | Unlock -> Send `0xA5 0x01 0x01` | Meter beeps/changes LCD icons |
| **R23** | Mode Override | Unlock -> Send `0xA5 0x02 0x0D` | Telemetry Byte 3 changes to `0D` |

---

## ⚠️ Risk Mitigation
- **Timeout Window:** State 41 times out in <50ms. R21 must use the Pico's hardware interrupts to respond to the `41` byte instantly.
- **Checksums:** All commands likely require a trailing checksum: `(Sum of bytes after 0xA5) & 0xFF`.

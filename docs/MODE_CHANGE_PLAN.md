# UT33C+ Mode Change Strategy (SD7501 Protocol)

This document outlines the tactical plan for remotely switching multimeter modes via the internal UART port, based on the identification of the **SD7501** chipset.

## 🎯 Objective
Transition the meter from its physical dial state (e.g., Continuity) to a software-controlled state (e.g., 20V DC) using the discovered **State 41** gateway.

---

## 🛠 Handshake Protocol (Updated for R34+)
Research indicates that the SD7501 follows a strict "Trigger-Acknowledge-Command" sequence, but it requires physical strapping and precise timing:

1.  **Strapping:** The user must manually HOLD the **SELECT** button.
2.  **Trigger:** Perform a Hard Power-OFF (Inverted Dual-Rail), wait 1.5s, then Power-ON.
3.  **Acknowledge:** Wait approximately **1.2 seconds** for the meter's bootloader to respond with Protocol Marker **`AB FD`** (or `41`).
4.  **Unlock:** Immediately send the **Binary Key `0xA5`**. This is the standard SDIC command prefix.
5.  **Confirm:** Wait for a response (Likely `0x06` ACK or a unique `AB CD 42...` frame).

---

## 🚀 Mode Change Command Set
Once the gateway is "Unlocked" (Step 4), we will test the following command structures:

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

## 📊 Experiment Roadmap (R34+)

| ID | Title | Logic | Target Outcome |
| :--- | :--- | :--- | :--- |
| **R34** | Precise Marker Response | Hard Reboot (w/ SELECT) -> Wait 1.2s for `AB FD` -> Send `0xA5 0x01 0x01` | Meter beeps/changes LCD icons |
| **R35** | Command Fuzzing | Target other payload variations for `0xA5` command set | Elicit `0x06` ACK |
| **R36** | Mode Override | Target Mode Byte override command | Telemetry Byte 3 changes |

---

## ⚠️ Risk Mitigation
- **Timeout Window:** The listener window after the `AB FD` marker is likely <50ms. R34 uses the Pico's hardware interrupts to respond instantly.
- **Checksums:** All commands likely require a trailing checksum: `(Sum of bytes after 0xA5) & 0xFF`.

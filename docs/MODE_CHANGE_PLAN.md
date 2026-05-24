# UT33C+ Mode Change Strategy (SD7501 Protocol)

This document outlines the tactical plan for remotely switching multimeter modes via the internal UART port, based on the identification of the **SD7501** chipset.

## Objective
Transition the meter from its physical dial state (e.g., Continuity) to a software-controlled state (e.g., 20V DC) using the discovered **State 41** gateway.

---

## Handshake Protocol (Updated through R85)
Research indicates that the SD7501 follows a strict "Trigger-Acknowledge-Command" sequence, but it requires physical strapping and precise timing. On this meter, **HOLD and SELECT refer to the same physical button**.

1.  **Strapping:** The user must manually hold the **HOLD/SELECT** button.
2.  **Trigger:** Perform a Hard Power-OFF (Inverted Dual-Rail), wait 1.5s, then Power-ON.
3.  **Early Spill:** On the external/opto UART, watch the first 0-100ms for early bytes such as `FF`, `F0`, or `F9`; R83 saw `F9 E0` passively at ~10ms.
4.  **Acknowledge:** Wait approximately **1.1-1.2 seconds** for the meter's bootloader to respond with Protocol Marker **`AB FD`**. No current serial-rig run has reproduced `41` in this hard-power path.
5.  **Unlock:** Immediately send the **Binary Key `0xA5`**. This remains the standard SDIC command-prefix candidate, but R34-R85 command probes have all been neutral so far.
6.  **Confirm:** Wait for a response such as `0x06` ACK, a unique `AB CD 42...` frame, or a telemetry mode-byte change.

---

## Mode Change Command Set
Once the gateway is "Unlocked" (Step 4), we will test the following command structures:

### Phase 1: Virtual Button Press (Safest)
Most SDIC chips allow simulating front-panel buttons via UART.
- **Command:** `0xA5 0x01 [Button_ID] [CS]`
- **Button IDs already probed:** `0x01` and `0x02` style candidates, plus direct-range probes, with no observed ACK or mode transition.
- **Remaining button IDs to consider:** wider sweep beyond the initial low IDs, but only after proving a repeatable early `F9` window.

### Phase 2: Direct Mode Injection
Forcing the "Mode Byte" (Byte 3 in the telemetry frame) to a new value.
- **Command:** `0xA5 0x02 [New_Mode] [CS]`
- **Target Modes:** `0x0D` (20V), `0x19` (Continuity).

### Phase 3: EEPROM Write (Advanced)
If the above fail, we may need to write directly to the temporary mode register in internal RAM/EEPROM.
- **Command:** `0xA5 0x10 [Address] [Value] [CS]`

---

## Experiment Roadmap (R34+)

| ID | Title | Logic | Target Outcome |
| :--- | :--- | :--- | :--- |
| **R34-R85** | Completed Marker + Command Probes | Hard reboot with and without HOLD/SELECT held; combined HOLD/SELECT + Backlight; device OFF with both buttons; inject after `FD`, `E0`, and known markers where appropriate | All command probes neutral; OFF state silent; useful marker map discovered |
| **Next** | Early Passive Repeat | HOLD/SELECT held in Continuity, external/opto capture of only first 0-100ms | Confirm whether early `F9` is repeatable |
| **Then** | Early F9 Probe | Only if `F9` repeats: inject minimal sync immediately after `F9` | Elicit `41`, ACK, or altered boot sequence |

---

## Risk Mitigation
- **Timeout Window:** The listener window after the `AB FD` marker is likely <50ms. R34 uses the Pico's hardware interrupts to respond instantly.
- **Checksums:** All commands likely require a trailing checksum: `(Sum of bytes after 0xA5) & 0xFF`.
- **Current Evidence:** `AB FD` response probes have been neutral. R84 showed HOLD/SELECT + Backlight does not improve the early route. R85 showed device OFF with both buttons is silent. The best remaining route is still the very early external `F9` window seen in R83 with HOLD/SELECT only.

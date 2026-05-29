# Protocol Map: UT33C+ Internal UART
This port auto-transmits raw data as soon as the meter is powered.

## Serial Settings
*   **Baud:** 2400
*   **Bits:** 8-N-1
*   **Mode:** Auto-Transmit (Continuous)

## Frame Structure (10 Bytes)
`[AB CD] [ID] [MODE] [B0] [B1] [B2] [B3] [B4] [CS]`

| Byte | Field | Description |
| :--- | :--- | :--- |
| 0-1 | Header | Fixed sync bytes: `AB CD`. |
| 2 | Protocol ID | `01` (Normal), `81` (Boot), `41` (Gateway / Ready). |

## Diagnostic & Boot Markers
During the initialization phase or when the HOLD/SELECT button is held, the MCU emits special markers:

| Marker | Meaning | Significance |
| :--- | :--- | :--- |
| **`AB FD`** | Bootloader Listener | Emitted ~1.1s after hard power-on. Primary trigger point for command injection attempts. |
| **`41`** | Gateway/Ready ID | Exposed in Byte 2 position after a NULL-glitched soft reset. Indicates the MCU is in a diagnostic listening state. |
| **`F9`** | Button-Active Marker | Observed in Byte 2 position when the HOLD/SELECT button is engaged during reset. |
| **`E0`** | Power-On Noise | First byte seen after power-up. Likely clock stabilization noise. |

## 9-Pad LCD/Matrix Specification
The 9 pads on the PCB carry multiplexed LCD signals and button matrix scans.
- **Frequency:** ~183 Hz (Common Multiplex Rate).
- **Behavior:** High-speed oscillation (GP17, 18, 19, 21) combined with static mode-state levels (GP16).
- **Interference:** Driving these pins causes the "All Segments Lit" state on the LCD. 

| 3 | Mode Byte | Dial range unit. Bit 7 (`0x80`) is a status flag (Seen in `8D`). |
| 4-7 | ADC Count | 32-bit Big Endian SIGNED integer (Internal counts). |
| 8 | Status | Flags (00=Normal, 04/03=Often seen in OL). |
| 9 | Checksum | `sum(Bytes 2..7) & 0xFF` (Excludes Status byte). |

## Confirmed Range Mappings
| Mode Byte | Range Name | Scaling / Formula |
| :--- | :--- | :--- |
| `07` | 2000mV DC | 1 count = 1.0mV |
| `0D` | 20V DC | 1 count = 0.01V |
| `15` | 200V DC | 1 count = 0.1V |
| `17` | 200mV DC | 1 count = 0.1mV (OL at 2080 counts) |
| `18` | 600V DC | 1 count = 1.0V |
| `12` | 200V AC | 1 count = 0.1V |
| `11` | 600V AC | 1 count = 1.0V |
| `0E` | 20k Ohm | 1 count = 0.01 kOhm |
| `1A` | 200k Ohm | 1 count = 0.1 kOhm |
| `1C` | 2M Ohm | 1 count = 0.01 MOhm |
| `19` | Continuity/Diode | See Special States below. |
| `16` | Celsius | 1 count = 0.1 deg C. Confirmed in Celsius mode; open input observed as `AB CD 01 16 00 00 FF 7F 01 95`. |
| `13` | Fahrenheit | `(count * 0.1 * 9/5) + 32` (Meter always sends Celsius) |

## Special States
*   **Over-Load (OL):** The UART signals OL with specific high values.
    *   **200mV Mode:** OL at or above 2080 counts.
    *   **Resistance/Continuity:** OL at or above 32512 counts (`7F00`).
*   **Continuity/Diode (Mode `19`):** This mode is contextual.
    *   If `count >= 0x7F00`: It's **Open Loop (OL)** for resistance.
    *   If `count < 3000`: It's a **Diode reading** in Volts (`count / 1000.0`).
    *   Otherwise: It's a **Continuity reading** in Ohms.
*   **Fahrenheit Mode:** The meter's display changes to deg F, but the UART *always* transmits the raw temperature in tenths of a degree Celsius. The receiving software must perform the conversion.
*   **Hardware Saturation:** When the ADC is fully pegged, the UART often sends counts of `7F FF`.
*   **Backlight + HOLD/SELECT:** In Continuity, holding Backlight together with HOLD/SELECT produced mixed external `AB ED`/`AB FD` boot markers and did not reproduce the early `F9` seen in R83.

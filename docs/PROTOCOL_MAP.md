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
| **`AB FD`** | Bootloader Listener | Emitted on the internal UART ~1.1s after hard power-on. Also emitted on the external/opto UART in every characterized non-Continuity mode so far, and in Continuity when the HOLD/SELECT button is held. Primary trigger point for command injection. |
| **`AB ED`** | External Continuity Boot Marker | Emitted on the external/opto UART in Continuity mode with no held button at the same boot offset. Confirmed repeatable in R45. |
| **`F9`** | Button-Active Marker | Observed in Byte 2 position when the HOLD/SELECT button is engaged during reset; R83 also saw passive external `F9` at ~10ms before `E0` with HOLD/SELECT held in Continuity. |
| **`F0`** | Early External Button-Held Spill | Occasionally observed before `E0` on the external/opto UART with HOLD/SELECT held in Continuity. |
| **`E0`** | Early Reset Junk | First byte seen after power-up. Likely clock stabilization noise. |

| 3 | Mode Byte | Dial range unit. Bit 7 (`0x80`) is a status flag (Seen in `8D`). |
| 4-7 | ADC Count | 32-bit Big Endian SIGNED integer (Internal counts). |
| 8 | Status | Flags (00=Normal, 04/03=Often seen in OL). |
| 9 | Checksum | `sum(Bytes 2..7) & 0xFF` (Excludes Status byte). |

## Confirmed Range Mappings
| Mode Byte | Range Name | Scaling / Formula |
| :--- | :--- | :--- |
| `07` | 2000mV DC | Observed in 2000m mode. Scaling still needs fixture validation. |
| `0D` | 20V DC | 1 count = 0.01V |
| `15` | 200V DC | Observed in 200V mode. Scaling still needs fixture validation. |
| `17` | 200mV DC | 1 count = 0.1mV (OL at 2080 counts) |
| `18` | 600V DC | Observed in 600V mode. Scaling still needs fixture validation. |
| `12` | 200V AC | Observed in 200VAC mode. Scaling still needs fixture validation. |
| `11` | 600V AC | Observed in 600VAC mode. Scaling still needs fixture validation. |
| `0E` | 20k Ohm | 1 count = 0.01kΩ |
| `1A` | 200k Ohm | 1 count = 0.1kΩ |
| `1C` | 2M Ohm | 1 count = 0.01MΩ |
| `19` | Continuity/Diode | See Special States below. |
| `16` | Celsius | 1 count = 0.1°C. Confirmed in Celsius mode; open input observed as `AB CD 01 16 00 00 FF 7F 01 95`. |
| `13` | Fahrenheit | `(count * 0.1 * 9/5) + 32` (Meter always sends Celsius) |

## Special States
*   **Over-Load (OL):** The UART signals OL with specific high values.
    *   **200mV Mode:** OL at or above 2080 counts.
    *   **Resistance/Continuity:** OL at or above 32512 counts (`7F00`).
*   **Continuity/Diode (Mode `19`):** This mode is contextual.
    *   If `count >= 0x7F00`: It's **Open Loop (OL)** for resistance.
    *   If `count < 3000`: It's a **Diode reading** in Volts (`count / 1000.0`).
    *   Otherwise: It's a **Continuity reading** in Ohms.
*   **Fahrenheit Mode:** The meter's display changes to °F, but the UART *always* transmits the raw temperature in tenths of a degree Celsius. The receiving software must perform the conversion.
*   **Hardware Saturation:** When the ADC is fully pegged, the UART often sends counts of `7F FF`.
*   **Backlight + HOLD/SELECT:** In Continuity, holding Backlight together with HOLD/SELECT produced mixed external `AB ED`/`AB FD` boot markers and did not reproduce the early `F9` seen in R83.

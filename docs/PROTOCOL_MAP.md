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
| 2 | Protocol ID | Always `01` in confirmed captures. |
| 3 | Mode Byte | Identifies the range/unit on the dial. |
| 4-7 | ADC Count | 32-bit Big Endian integer (Internal counts). |
| 8 | Status | Flags (00=Normal, 04/03=Often seen in OL). |
| 9 | Checksum | `sum(Bytes 2..8) & 0xFF`. |

## Confirmed Range Mappings
| Mode Byte | Range Name | Scaling / Formula |
| :--- | :--- | :--- |
| `0D` | 20V DC | 1 count = 0.01V |
| `17` | 200mV DC | (count - 2000) * 0.1mV |
| `0E` | 20k Ohm | 1 count = 0.01kΩ |
| `1A` | 200k Ohm | 1 count = 0.1kΩ |
| `1C` | 2M Ohm | 1 count = 0.001MΩ |
| `19` | Continuity | Raw Counts (<1000 = Beep) |
| `16` | Celsius | 1 count = 0.1°C |
| `13` | Fahrenheit | 1 count = 1.0°F |

## Special States
*   **Software OL:** Meter displays "OL" when specific thresholds are met (e.g., ~2080 counts in 200mV mode). UART sends stable high values.
*   **Hardware Saturation:** When the ADC is fully pegged, UART sends `7F FF` or `FF FF`.
*   **Startup Signature:** During Pad 2 reset, the meter briefly outputs `01 00 00 81 01 00` before standard frames begin.

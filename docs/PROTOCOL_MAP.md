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
| `17` | 200mV DC | 1 count = 0.1mV (OL at 2080 counts) |
| `0E` | 20k Ohm | 1 count = 0.01kΩ |
| `1A` | 200k Ohm | 1 count = 0.1kΩ |
| `1C` | 2M Ohm | 1 count = 0.01MΩ |
| `19` | Continuity/Diode | See Special States below. |
| `16` | Celsius | 1 count = 0.1°C |
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

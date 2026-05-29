# Protocol Map: UT33C+ Telemetry

The UT33C+ auto-transmits raw binary data continuously while powered on.

## Serial Settings
*   **Baud Rate:** 2400
*   **Data Bits:** 8
*   **Parity:** None
*   **Stop Bits:** 1

## Frame Structure (10 Bytes)
Every reading is packaged into a 10-byte frame:
`[AB CD] [ID] [MODE] [B0] [B1] [B2] [B3] [STATUS] [CS]`

| Byte | Field | Description |
| :--- | :--- | :--- |
| `0-1` | Header | Fixed sync bytes: `0xAB 0xCD`. |
| `2` | Protocol ID | `0x01` indicates normal operating mode. |
| `3` | Mode Byte | Defines the current dial range/unit (see table below). |
| `4-7` | ADC Count | 32-bit Big Endian SIGNED integer representing the raw internal counts. |
| `8` | Status | Flags (e.g., `0x00` = Normal, `0x04` or `0x03` = Often seen during Over-Load). |
| `9` | Checksum | `sum(Bytes 2..7) & 0xFF` (Note: The Status byte is *excluded* from the checksum). |

## Confirmed Range Mappings (Byte 3)

| Mode Byte | Range Name | Value Calculation |
| :--- | :--- | :--- |
| `0x07` | 2000mV DC | 1 count = 1.0 mV |
| `0x0D` | 20V DC | 1 count = 0.01 V |
| `0x15` | 200V DC | 1 count = 0.1 V |
| `0x17` | 200mV DC | 1 count = 0.1 mV *(Over-Load at 2080 counts)* |
| `0x18` | 600V DC | 1 count = 1.0 V |
| `0x12` | 200V AC | 1 count = 0.1 V |
| `0x11` | 600V AC | 1 count = 1.0 V |
| `0x1D` | 200 Ohm | 1 count = 0.1 Ohm |
| `0x1E` | 2000 Ohm | 1 count = 1.0 Ohm |
| `0x0E` | 20k Ohm | 1 count = 0.01 kOhm |
| `0x1A` | 200k Ohm | 1 count = 0.1 kOhm |
| `0x1C` | 2M Ohm | 1 count = 0.01 MOhm |
| `0x16` | Celsius | 1 count = 0.1 °C |
| `0x13` | Fahrenheit | `(count * 0.1 * 9/5) + 32` *(The meter always transmits Celsius counts over UART, even when the screen shows Fahrenheit).* |
| `0x19` | Continuity/Diode | *See Special States below.* |

## Special States

### Over-Load (OL)
When the meter probes measure something beyond the current range, the UART signals an "Over-Load" state. The software dashboard handles this by looking for specific extreme count values (e.g., `0x7F00` or `32512` in Resistance modes, or `>= 2080` in the 200mV mode).

### Continuity & Diode Mode (`0x19`)
This mode is contextual and shares a single Mode Byte. The Python decoder interprets it based on the ADC count:
*   If `count >= 32512`: The probes are open. Display shows **OL**.
*   If `count < 3000`: The meter is reading a voltage drop across a diode. Divide count by 1000 to get **Volts**.
*   Otherwise: The meter is measuring low resistance. Display the count directly as **Ohms** (this is when the buzzer sounds).

### Hardware Saturation
When the ADC is completely pegged to its maximum physical limit (beyond standard OL), the UART will stream `7F FF` in the count bytes.

---
*Note: Early research investigated remote command injection (e.g., changing modes via UART). This path is locked behind an unknown OEM authorization sequence. The meter is effectively a read-only telemetry device.*

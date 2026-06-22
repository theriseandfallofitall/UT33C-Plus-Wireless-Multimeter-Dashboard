# UT33C+ telemetry protocol

The UT33C+ sends raw binary telemetry continuously while it is powered on.

## Serial settings

- Baud: 2400
- Data bits: 8
- Parity: none
- Stop bits: 1

## Frame format

Each reading is a 10-byte frame:

```text
[AB CD] [ID] [MODE] [B0] [B1] [B2] [B3] [STATUS] [CS]
```

| Byte | Field | Notes |
| --- | --- | --- |
| `0-1` | Header | Fixed sync bytes: `0xAB 0xCD`. |
| `2` | Protocol ID | `0x01` in normal operation. |
| `3` | Mode | Dial range / unit. See the table below. |
| `4-7` | ADC count | 32-bit big-endian signed integer. |
| `8` | Status | Status flags. `0x00` is normal. `0x04` and `0x03` often show up around overload states. |
| `9` | Checksum | `sum(bytes 2..7) & 0xFF`. The status byte is not included. |

## Confirmed mode mappings

| Mode | Range | Calculation |
| --- | --- | --- |
| `0x07` | 2000mV DC | 1 count = 1.0 mV |
| `0x0D` | 20V DC | 1 count = 0.01 V |
| `0x15` | 200V DC | 1 count = 0.1 V |
| `0x17` | 200mV DC | 1 count = 0.1 mV. Overload appears around 2080 counts. |
| `0x18` | 600V DC | 1 count = 1.0 V |
| `0x12` | 200V AC | 1 count = 0.1 V |
| `0x11` | 600V AC | 1 count = 1.0 V |
| `0x1D` | 200 ohm | 1 count = 0.1 ohm |
| `0x1E` | 2000 ohm | 1 count = 1.0 ohm |
| `0x0E` | 20k ohm | 1 count = 0.01 kOhm |
| `0x1A` | 200k ohm | 1 count = 0.1 kOhm |
| `0x1C` | 2M ohm | 1 count = 0.01 MOhm |
| `0x16` | Celsius | 1 count = 0.1 °C |
| `0x13` | Fahrenheit | The meter still sends Celsius counts over UART. Convert with `(count * 0.1 * 9/5) + 32`. |
| `0x19` | Continuity / diode | Shared mode. See below. |

## Special states

### Overload

When the probes exceed the selected range, the meter reports overload. The decoder checks for the count patterns seen in captures, including `0x7F00` / `32512` in resistance modes and `>= 2080` in 200mV mode.

### Continuity and diode mode (`0x19`)

The same mode byte covers continuity and diode mode. The decoder decides what to show from the ADC count:

- `count >= 32512`: open probes, display `OL`.
- `count < 3000`: diode voltage drop. Divide by 1000 for volts.
- Anything else: low resistance in ohms, which is also when the buzzer sounds.

### Hardware saturation

If the ADC is completely pegged beyond the normal overload state, the count bytes stream as `7F FF`.

## Read-only behaviour

I did look at remote control over UART, including changing modes from software. That route appears to be locked behind an undocumented OEM authorization sequence. For this project, the UT33C+ is a read-only telemetry device.

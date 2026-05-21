# UNI-T UT33C+ Hidden UART Protocol Notes

## Status

This document records the current reverse-engineering findings for a UNI-T UT33C+ multimeter internal UART stream.

The protocol has been partially decoded from live captures. The findings below are confirmed for DC voltage captures supplied so far, but are not yet complete for all modes, ranges, and annunciator states.

## Executive Summary

The useful telemetry stream is at:

```text
2400 baud, 8 data bits, no parity, 1 stop bit
```

Earlier captures at `9600 baud` produced repeatable but misleading data. Those bytes appeared segment-like, but later 2400 baud captures showed a clean 10-byte telemetry frame.

The frame carries a signed integer measurement value, a checksum, a fixed sync/footer marker, and mode/range bytes.

## Confirmed Frame Format

A complete frame is 10 bytes:

```text
B0 B1 B2 B3 B4 CS AB CD MODE RANGE
```

Known examples:

```text
00 00 04 C0 00 D2 AB CD 01 0D  -> +12.16 V on 20 V DC range
FF FF FB 40 03 47 AB CD 01 0D  -> -12.16 V on 20 V DC range
FF FF FF 87 03 9A AB CD 01 15  -> -12.1 V on 200 V DC range
```

## Field Meanings

| Byte(s) | Meaning | Status |
|---|---|---|
| `B0 B1` | Sign extension / upper word | Confirmed pattern |
| `B2 B3` | Signed 16-bit measurement count | Confirmed |
| `B4` | Sign/status byte: observed `00` for positive, `03` for negative | Partially confirmed |
| `CS` | Checksum | Confirmed |
| `AB CD` | Fixed frame marker | Confirmed |
| `MODE` | Mode identifier; observed `01` for DC voltage | Partially confirmed |
| `RANGE` | Range / decimal-placement identifier | Partially confirmed |

## Value Encoding

The measurement is encoded in bytes `B2 B3` as a signed 16-bit integer.

```text
raw = signed16((B2 << 8) | B3)
```

Then apply a scale factor based on `RANGE`.

Confirmed scales:

| Mode | Range byte | Range | Scale | Example |
|---|---:|---|---:|---|
| DC voltage | `0D` | 20 V | divide by 100 | `0x04C0 = 1216 -> 12.16 V` |
| DC voltage | `15` | 200 V | divide by 10 | `0xFF87 = -121 -> -12.1 V` |

## Checksum

The checksum is the low byte of the sum of all frame bytes except the checksum byte itself.

```text
CS = (B0 + B1 + B2 + B3 + B4 + MODE + RANGE) & 0xFF
```

## Confirmed Serial Behaviour

Observed update interval is approximately 0.47 to 0.50 seconds per frame, or roughly 2 frames per second.

## Confirmed DC Voltage Examples

| Frame | Decoded value |
|---|---:|
| `00 00 01 4C 00 5B AB CD 01 0D` | +3.32 V |
| `00 00 01 AD 00 BC AB CD 01 0D` | +4.29 V |
| `00 00 04 C0 00 D2 AB CD 01 0D` | +12.16 V |
| `FF FF FB 40 03 47 AB CD 01 0D` | -12.16 V |
| `FF FF FF 87 03 9A AB CD 01 15` | -12.1 V |

## What Is Confirmed

- UART telemetry exists.
- Correct baud is `2400`.
- Frame length is `10` bytes.
- Frame marker is `AB CD`.
- DC voltage mode byte is currently observed as `01`.
- Signed values are supported.
- Negative values use signed 16-bit two's-complement in `B2 B3`.
- Positive and negative frames differ in the sign/status bytes.
- 20 V range uses `/100`.
- 200 V range uses `/10`.
- Checksum formula is confirmed.

## Still To Complete

Capture and confirm:

- 200 mV, 2 V, 600 V DC ranges if present and safe.
- AC voltage.
- DC current ranges.
- Resistance.
- Continuity.
- Diode test.
- Temperature.
- Overload / OL.
- Hold mode.
- Low battery annunciator.
- Startup/shutdown frames.

Determine meanings for:

```text
B0 B1
B4
MODE
RANGE
```

## Recommended Capture Format

For future work, capture raw 2400 baud bytes as complete frame lines:

```text
00 00 04 C0 00 D2 AB CD 01 0D
```

## Safety Notes

The UART/FTDI ground may be electrically connected to the meter circuit. When measuring high voltage or mains:

- Do not connect the meter to a grounded PC USB port unless isolation is understood.
- Prefer a battery-powered laptop or isolated USB adapter.
- Use an opto-isolated UART bridge for mains-related measurements.
- Do not touch the meter PCB while connected to live circuits.

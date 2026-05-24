# UT33C+ / SD7501 Mode-Selection Research Notes

## Objective

Find how the multimeter selects measurement modes/ranges, especially whether mode selection can be controlled through UART or whether it is determined by the physical rotary-switch matrix.

## Current best conclusion

The mode-selection switching is most likely **hardware switch-matrix based**, not UART-command based.

The UART telemetry appears to report the mode/range after the MCU has read the rotary switch state. The useful target is therefore the rotary/function switch matrix and its GPIO pins, not only the UART RX line.

## Primary sources

- SDIC SD7501 official product page: https://sdicmicro.cn/en/product/detail/id/10455.html
- SDIC SD7501 datasheet PDF: https://sdicmicro.cn/upload/img/2021-08/611cad9c519ad.pdf
- SDIC product/download index: https://sdicmicro.cn/en/service/index.html
- SDIC multimeter SoC product family page: https://sdicmicro.cn/en/product/index/pid/10011.html
- JLCPCB SD7501 component page: https://jlcpcb.com/partdetail/406575-SD7501/C414115
- SDIC product-selection PDF: https://sdicmicro.cn/upload/img/2023-05/64633c119f860.pdf

## Evidence from SD7501 datasheet

The SD7501 is a multimeter SoC with:

- 24-bit ADC
- 16 KB OTP memory
- 256 B SRAM
- UART
- LCD driver
- GPIO ports
- selectable pull-ups
- power-on reset / low-voltage detection
- 2.4 V to 3.6 V operating range
- LQFP64 package

Relevant pins from the SD7501 datasheet:

| Pin / signal | Relevance |
|---|---|
| P30 / RXD | UART receive input |
| P31 / TXD | UART transmit output |
| RST_B | Active-low reset input |
| P11 / P12 / P13 / P14 | GPIO / interrupt-capable inputs likely involved in button or function selection |
| P20 / P21 / P22 / P23 / P24 | GPIO / interrupt-capable inputs likely involved in function-selection matrix |
| Programming pins around P32-P35 area | Separate serial/OTP programming path, probably not the same as normal UART |

The typical application schematic in the datasheet shows a **function-selection block** connected to GPIO lines, with the logic convention:

```text
Open  = 1
Close = 0
```

This strongly suggests the rotary switch pulls selected matrix lines low, and the firmware decodes the resulting pattern.

## Evidence from current experiments

Source context: uploaded experiment notes in this conversation.

Known observed UART/range behavior:

| Dial mode | Observed normal frame / range byte |
|---|---|
| 200 mV DC | `AB CD 01 17 ...` |
| 2000 mV DC | `AB CD 01 07 ...` |
| 20 V DC | `AB CD 01 0D ...` |
| 200 V DC | `AB CD 01 15 ...` |
| Continuity | External boot/listener marker often `AB ED` |
| Other voltage modes | External boot/listener marker often `AB FD` |

Other relevant experiment findings:

- Normal protocol ID: `01`
- Boot/status protocol ID: `81`
- Boot/status period lasts roughly 500 ms after power cycle or Pad 2 reset
- UART link is physically valid because injected `55 AA` appeared as reflection artifacts
- Hard power reset is more reliable than soft reset for entering diagnostic windows
- Physical button hold appears mandatory for diagnostic gateway entry
- `AB FD` / `AB ED` markers are mode-dependent
- The diagnostic window is very short after marker detection
- UART command probes so far remained neutral; no confirmed mode-switch command was found

## Practical implication

UART is probably not the mode-control interface.

More likely model:

```text
Rotary switch contacts
        ↓
GPIO switch matrix: P20-P24 and/or P11-P14
        ↓
SD7501 firmware decodes selected function/range
        ↓
UART telemetry reports decoded mode byte
```

So bytes such as `07`, `0D`, `15`, and `17` are probably **reported results of switch state**, not commands that directly select the range.

## Recommended mapping procedure

### 1. Map the rotary switch with power removed

Use continuity mode on a second meter.

For each dial position, record which rotary switch pads are shorted.

Suggested table:

| Dial position | Contact A | Contact B | Contact C | Contact D | Contact E | Contact F | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| OFF | | | | | | | |
| Continuity | | | | | | | |
| 200 mV | | | | | | | |
| 2000 mV | | | | | | | |
| 20 V | | | | | | | |
| 200 V | | | | | | | |
| Ω | | | | | | | |
| Diode | | | | | | | |
| Current ranges | | | | | | | |

### 2. Probe candidate MCU pins live

With the meter powered, probe these pins relative to meter logic ground:

```text
P11
P12
P13
P14
P20
P21
P22
P23
P24
```

Expected behavior:

```text
Open switch contact  -> logic high
Closed switch contact -> logic low
```

Do not drive the pins at first. Only observe.

### 3. Build a GPIO truth table

Record each pin state per dial position.

Suggested table:

| Dial position | P11 | P12 | P13 | P14 | P20 | P21 | P22 | P23 | P24 | UART mode/range byte |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Continuity | | | | | | | | | | |
| 200 mV | | | | | | | | | | `17` |
| 2000 mV | | | | | | | | | | `07` |
| 20 V | | | | | | | | | | `0D` |
| 200 V | | | | | | | | | | `15` |
| Other | | | | | | | | | | |

### 4. Emulate switch closures safely

If you want to force a mode electronically, emulate the rotary switch contacts using open-drain or isolated switching.

Preferred methods:

- small analog switches
- opto-MOS / photoMOS relays
- reed relays
- N-MOSFET open-drain pull-downs, only if grounds and voltage levels are confirmed safe

Avoid:

- directly driving MCU pins high
- injecting external 3.3 V into unknown switch lines
- shorting analog measurement paths without understanding the front-end resistor network
- changing switch state while high voltage is connected to the input jacks

Safe control model:

```text
MCU internal/external pull-up keeps line high
external emulation only pulls selected line low
external emulation otherwise leaves line floating/open
```

## Important distinction

There are probably two different things that look related but are not the same:

### Mode selection

Likely done through the rotary switch matrix.

```text
physical contact pattern -> GPIO state -> firmware mode decode
```

### UART telemetry / diagnostic state

Likely reports current state or exposes limited factory/diagnostic behavior.

```text
firmware state -> UART frame
```

Do not assume a UART byte that appears in telemetry is also a valid command byte.

## Most useful next experiment

Instead of more UART fuzzing, run a physical switch-matrix correlation test:

1. Pick 4 known dial modes:
   - 200 mV
   - 2000 mV
   - 20 V
   - 200 V

2. For each mode:
   - capture UART normal frame
   - record range byte
   - probe P11-P14 and P20-P24
   - record which switch contacts are closed

3. Compare:

```text
rotary contact pattern
GPIO logic pattern
UART range byte
```

This should identify the actual mode-selection mechanism.

## Working hypothesis

For UT33C+ / SD7501-like meters:

```text
Mode byte = decoded rotary-switch state + firmware status flags
```

Example:

```text
0D = 20 V mode
8D = 20 V mode + high-bit status flag
```

The `0x80` high-bit flip seen in `0D -> 8D` may indicate a status condition such as lock, diagnostic activity, overrange, hold, or internal state flag. It should not be interpreted as a separate physical range without more evidence.

## Actionable next steps

1. Photograph both PCB sides around the rotary switch and SD7501.
2. Identify SD7501 pin 1 orientation.
3. Trace P20-P24 and P11-P14 to the rotary switch or button network.
4. Create a continuity map of the switch contacts with power removed.
5. Create a live logic-state table for every dial position.
6. Match each logic-state pattern to the UART mode/range byte.
7. Only after that, emulate one known safe mode using open-drain pull-downs or analog switches.

## Key warning

The SD7501 datasheet confirms UART exists, but it does not provide a public UART mode-selection command set. The datasheet points more strongly toward a hardware GPIO selection matrix. Therefore, for mode switching, the highest-value work is switch-matrix reverse engineering, not UART bootloader fuzzing.

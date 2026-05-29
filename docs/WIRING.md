# Hardware Wiring Guide

The UT33C+ is built around an SD7501 (or similar) multimeter IC. This chip continuously streams out all of its telemetry via a hidden UART port as soon as the meter is turned on.

By connecting three wires to the main PCB, I can broadcast this data over Bluetooth.

## Locating the Pads

Open the back of your UT33C+ and locate the main PCB. 

![Internal Wiring](..images/wiring.jpg)

### 1. The Internal UART (Telemetry Stream)
Near the center/bottom of the board, you will find a set of test pads.
- **Internal TX:** This pad transmits the 2400 baud, 8N1 binary data stream. **Connect this to your Bluetooth module's `RXD` pin.**
- **Internal RX:** This pad is a listener, but exhaustive hardware fuzzing has confirmed that command injection (remote control) is locked behind a proprietary OEM authorization key. **Do not connect anything to this pad.**

### 2. Power and Ground
To power your Bluetooth module, you will need to tap into the meter's power rails.
- **GND:** Connect this to your module's `GND` pin. (Note: This is electrically identical to the `COM` probe jack).
- **VCC (3.0V):** The meter runs on two AAA batteries, providing ~3.0V. Connect this to your module's `VCC` pin.
  - *Crucial Note:* Many ZS-040 (HC-05/06) modules are designed for 3.6V - 6V logic and have onboard regulators. While some will operate directly on 3.0V, their range and stability might suffer. If your module drops connection, you may need to bypass its onboard 3.3V regulator or use a tiny 3V-to-5V step-up converter.

## What NOT to Touch

During my reverse-engineering phase, I mapped out several other pads on the board. You should **avoid connecting anything to these**:

- **The 9-Pad Interface:** There is a group of 9 pads near the top/rotary dial. **Do not solder to these.** These are the multiplexed LCD segment and keypad scanning lines (running at ~183 Hz). Shorting them or driving them with a microcontroller will interfere with the LCD glass and cause all segments to light up, potentially damaging the driver.
- **Pad 1 (Soft Reset) & Pad 2 (Hard Reset):** These were used to trigger timing attacks against the IC's bootloader. They are not useful for general telemetry.

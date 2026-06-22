# Reverse engineering notes

## How this started

This was not meant to be a reverse-engineering project. The continuity buzzer on the UT33C+ is just obnoxiously loud.

I opened the meter to cover the buzzer with tape and noticed a row of unlabeled test pads, including TX and RX. I put a logic analyzer on them, then tried a UART adapter. The meter was already streaming its readings at 2400 baud.

So the quick buzzer fix turned into a wireless dashboard.

## 1. UART command injection

Goal: use the internal `RX` pad to send commands such as `SELECT` or `HOLD` directly to the meter.

What I tried:

- Standard UNI-T-looking command frames, including `AB 01` for select.
- 2400, 4800, and 9600 baud.
- Sending commands after the telemetry stream had started.

Result: no response. Once normal telemetry starts, the chip ignores the RX line, or the input path is locked.

## 2. Timing and reset attacks

Goal: inject a key during the tiny window when the chip first wakes up.

I used a Pi Pico test rig to automate power cycles and reset pulses, then blasted the RX line with null bytes and likely OEM prefixes such as `0xA5 0x5A` as soon as the first byte appeared.

This did expose a hidden protocol ID: `41`, which looked like a gateway mode. With the right reset glitch, the meter switched from ID `01` to ID `41`.

That still was not enough. In that state the meter expected a specific multi-byte authorization key. I did not find it, and brute forcing it was not realistic.

## 3. The 9-pad matrix

Goal: find out whether the 9 unlabeled pads near the rotary dial were a programming or control header.

I soldered to the pads and used the Pico as a 360kHz logic probe. The signals were oscillating at about 183 Hz. Driving them directly caused the LCD to enter an "all segments lit" state.

Conclusion: those pads are for the LCD glass and keypad scanning. They are not a digital control port.

## 4. Optical port probing

Goal: use the external opto-port, normally used for PC-Link, to inject commands.

I monitored the external UART pads while holding different button combinations during boot. Holding `HOLD/SELECT` changed the external boot marker from `AB ED` to `AB FD`, which looked like a listener marker.

It still behaved as read-only without the proprietary handshake.

## Where this leaves things

The telemetry path is wide open and easy to decode. The command path is deliberately locked down.

If remote control is ever worth doing, the practical options are physical bypasses:

1. Optocouplers or analog switches across the button traces.
2. A servo to turn the rotary dial.

For now, the cleanest version of this project is the simple one: listen to the meter, do not try to control it.

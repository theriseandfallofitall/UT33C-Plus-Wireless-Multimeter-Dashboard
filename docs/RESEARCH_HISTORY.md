# Research History: Reverse Engineering the UT33C+

## The Origin Story
This project did not start as a sophisticated reverse-engineering operation. It started because I was frustrated. 

The continuity buzzer on the UT33C+ is so bloody loud. It was so loud that I eventually snapped and opened the meter to cover the buzzer with tape. 

While I was inside the casing, I noticed a row of unlabeled test pads on the PCB as well as TX and RX. bbed my logic analyzer. I quickly popped on uart adapter and got some data. 

That data turned out to be a continuous 2400-baud UART stream of every single measurement the meter was making. What began as a quick fix with tape turned into this wireless dashboard.

## 1. UART Command Injection
**Goal:** Use the `Internal RX` pad to send commands (e.g., `SELECT`, `HOLD`) directly to the MCU.

- **Attempted:** I sent standard UNI-T command frames (like `AB 01` for Select) at various baud rates (2400, 4800, 9600).
- **Result:** **FAILED.** The MCU ignored all input on the RX line once the primary telemetry stream started.
- **Discovery:** The RX path appears to be physically disabled or software-locked immediately after the boot sequence.

## 2. Timing & Reset Attacks
**Goal:** Inject a "Magic Key" during the sub-millisecond window when the chip first wakes up.

- **Attempted:** Using a Pi Pico as a high-speed HIL (Hardware-In-the-Loop) rig, I automated power cycles and reset pulses. I blasted the RX line with NULL bytes and various OEM prefixes (like `0xA5 0x5A`) the instant the chip emitted its first byte.
- **Discovery:** I successfully exposed a hidden **Protocol ID `41`** (Gateway Mode). When glitched correctly during a soft reset, the meter would switch its ID from `01` to `41`.
- **Result:** **LOCKED.** Even in the `41` state, the meter required a specific multi-byte authorization key that is not documented and could not be brute-forced.

## 3. The 9-Pad Matrix
**Goal:** Identify a secondary programming or control header.

- **Attempted:** Soldered to 9 unlabeled pads on the PCB, suspecting they might be a JTAG, SWD, or static mode-selection interface.
- **Investigation:** I used the Pico as a 360kHz logic probe to analyze the signals. 
- **Result:** **LCD MATRIX.** The pins were oscillating at ~183 Hz. Driving them directly caused the "All Segments Lit" state on the LCD.
- **Conclusion:** These pads are the multiplexed drive lines for the LCD glass and the keypad scanning matrix. They are not a digital control port.

## 4. Optical Port Probing
**Goal:** Use the external opto-port (typically used for PC-Link) to inject commands.

- **Attempted:** Monitored the external UART pads while holding various button combinations during boot.
- **Discovery:** Holding `HOLD/SELECT` during power-on changes the external boot marker from `AB ED` to `AB FD` (The "Listener" marker).
- **Result:** **READ-ONLY.** Like the internal pads, the external port is highly resistant to injection without the proprietary OEM handshake.

## Final Conclusion
The SD7501 chipset used in the "Plus" series multimeters has been intentionally hardened against unauthorized remote control. While the **Telemetry (Out)** path is wide open and easy to decode, the **Command (In)** path is gated by an encrypted or password-protected bootloader.

Remote control is only feasible through **analog bypass**:
1. Soldering optocouplers or analog switches across the physical button traces.
2. Using a servo motor to physically turn the rotary dial.

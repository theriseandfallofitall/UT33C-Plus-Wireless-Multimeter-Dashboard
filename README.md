# UT33C+ Wireless Multimeter Dashboard

This project upgrades a standard UNI-T UT33C+ digital multimeter into a wireless, data-logging smart meter using a simple, cheap Bluetooth module.

By tapping into the multimeter's hidden internal telemetry stream discovered purely by accident while I was trying to tape over the continuity buzzer this software provides a realtime dashboard, data logging, and interactive graphing on your PC.

![In Action](images/in_action.jpg)

## Core Features

- **No Microcontrollers Required:** Connect a simple ZS-040 (HC-05/HC-06) Bluetooth module directly to the meter's PCB.
- **Auto-Connect:** Automatically discovers and connects to your paired Bluetooth module.
- **Overlay Mode:** Tear off a transparent, borderless, always on top window to monitor readings while you work or game.
  ![Transparent Overlay](images/transparent_overlay.png)
- **Full Decoding:** Real-time decoding of DC/AC Voltage, Resistance, Continuity, Diode drops, and Temperature.
- **Snapshot History:** Save and label instantaneous readings with a single click.
  ![Snapshots](images/snapshots.png)
- **CSV Data Logging:** Log long-term trends to timestamped CSV files for later analysis.
  ![Logging](images/logging.png)

## How to Build Yours

1. Hardware Mod: Wire a generic Bluetooth module to the meter's internal UART pad. It takes 3 wires (TX, VCC, GND).
   - Read the [Hardware Wiring Guide](docs/WIRING.md) to locate the pads.
   - Read the [Bluetooth Setup Guide](docs/BT_SETUP.md) to configure your module.
2. Install Software: Ensure you have Python 3 installed.
   ```bash
   pip install pyserial matplotlib
   ```
3. Launch the Dashboard:
   ```bash
   python app.py
   ```

### Command Line Alternative
To log telemetry to CSV without the graphical UI:
```bash
python ut33c_logger.py
```

## Documentation

- [**Hardware Wiring Guide (WIRING.md)**](docs/WIRING.md): Where to solder your wires and what to avoid (like the 9-pad LCD matrix).
- [**Bluetooth Setup Guide (BT_SETUP.md)**](docs/BT_SETUP.md): How to program your ZS-040 module to 2400 baud so it can talk to the meter.
- [**Protocol Reference (PROTOCOL.md)**](docs/PROTOCOL.md): A detailed map of the 10 byte binary telemetry frames.
- [**Research History (RESEARCH_HISTORY.md)**](docs/RESEARCH_HISTORY.md): A technical log of the failed attempts to gain remote control (UART fuzzing, timing attacks, etc.).

## Safety Warning
The internal ground of the multimeter is electrically connected to the COM probe. Never connect the meter to a grounded PC via USB while measuring high voltages. 
This is why the Bluetooth modification is highly recommended it provides complete galvanic isolation, keeping your PC safe.

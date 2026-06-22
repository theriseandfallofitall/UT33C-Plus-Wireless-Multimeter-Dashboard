# Bluetooth setup

A cheap ZS-040 / HC-05 Bluetooth serial module is enough to make the UT33C+ wireless. It also keeps the meter electrically isolated from your PC, which matters if the probes ever touch anything nasty.

## Set the module to 2400 baud first

The meter's UART runs at 2400 baud. Most Bluetooth serial modules ship at 9600 baud, so configure the module before you solder it into the meter. If you skip this, the dashboard will only see scrambled data.

You need a USB-TTL serial adapter such as an FT232 or CH340.

### ZS-040 / HC-05 setup

1. Connect the Bluetooth module to the USB-TTL adapter:
   - TX -> RX
   - RX -> TX
   - VCC -> 5V
   - GND -> GND
2. Hold the small button on the Bluetooth module while plugging the USB adapter into your PC. The LED should blink slowly, roughly once every two seconds. That means it is in AT mode.
3. Open a serial terminal such as PuTTY, CoolTerm, or the Arduino Serial Monitor.
4. Connect to the USB-TTL adapter at 38400 baud. Set the terminal to send both `CR` and `LF` at the end of each line.
5. Set the UART speed:
   ```text
   AT+UART=2400,0,0
   ```
   The module should reply with `OK`.
6. Give the module a name the dashboard can recognise:
   ```text
   AT+NAME=UT33C_MultiMeter
   ```
   Again, you should get `OK` back.

## Wire it into the meter

After the module is configured, unplug it from the USB adapter and follow the [hardware wiring guide](WIRING.md).

## Pair it with your PC

1. Turn on the multimeter. The Bluetooth module LED should flash quickly.
2. Open Bluetooth settings on your computer.
3. Add a new Bluetooth device and pair with `UT33C_MultiMeter`, or whatever name you chose.
   - The default PIN is usually `1234` or `0000`.
4. Windows will create a "Standard Serial over Bluetooth link" COM port in the background.

## Start the dashboard

Run:

```bash
python app.py
```

If the module is named `UT33C_MultiMeter`, the dashboard should find the Bluetooth COM port and connect by itself.

![Settings interface](../images/settings.png)

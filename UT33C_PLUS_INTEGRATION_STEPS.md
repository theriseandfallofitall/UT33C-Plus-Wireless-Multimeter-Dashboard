# UNI-T UT33C+ Integration Methods

Confirmed serial settings:

```text
2400 baud, 8N1, no flow control
```

Confirmed frame:

```text
B0 B1 B2 B3 B4 CS AB CD MODE RANGE
```

Checksum:

```text
CS = (B0 + B1 + B2 + B3 + B4 + MODE + RANGE) & 0xFF
```

## Safety First

The meter UART ground may be connected to the measurement circuitry. For mains or high-voltage work, use galvanic isolation or an isolated USB-UART adapter.

## Method 1: USB Serial Logger

### Hardware

```text
Meter GND -> USB-UART GND
Meter TX  -> USB-UART RX
Meter RX  -> leave unconnected initially
Meter VCC -> do not connect unless verified
```

### Linux

```bash
python3 -m pip install pyserial
python3 ut33c_plus_logger.py --port /dev/ttyUSB0
```

If permission is denied:

```bash
sudo usermod -aG dialout "$USER"
```

Log out and back in.

### Windows

```powershell
py -m pip install pyserial
py .\ut33c_plus_logger.py --port COM5
```

### CSV Logging

```bash
python3 ut33c_plus_logger.py --port /dev/ttyUSB0 --csv readings.csv
```

## Method 2: sigrok Decoder

Recommended path:

1. Configure UART decoder at `2400 8N1`.
2. Feed UART RX bytes into a UT33C+ protocol decoder.
3. Maintain a rolling buffer.
4. Find `AB CD` at byte positions 6 and 7.
5. Verify checksum.
6. Decode signed value and range scale.
7. Emit annotations for raw frame, checksum, mode, range, raw count, and value.

Known table:

```text
MODE  RANGE  SCALE  UNIT
01    0D     /100   V
01    15     /10    V
```

Write the sigrok decoder after capturing the remaining modes/ranges, unless you only need DC voltage support.

## Method 3: ESP32 Wireless Bridge

### Wiring

```text
Meter TX  -> ESP32 RX, e.g. GPIO16
Meter GND -> ESP32 GND
```

Use isolation for hazardous measurements.

### ESP32 Arduino Decoder Skeleton

```cpp
#include <Arduino.h>

HardwareSerial MeterSerial(2);
const int RX_PIN = 16;
const int TX_PIN = 17;
uint8_t buf[64];
size_t len = 0;

int16_t signed16(uint16_t v) { return (v & 0x8000) ? (int16_t)(v - 0x10000) : (int16_t)v; }

bool checksum_ok(const uint8_t *f) {
  uint8_t cs = f[0] + f[1] + f[2] + f[3] + f[4] + f[8] + f[9];
  return cs == f[5];
}

bool decode_frame(const uint8_t *f, float &value, const char* &unit) {
  if (f[6] != 0xAB || f[7] != 0xCD || !checksum_ok(f)) return false;
  int16_t raw = signed16(((uint16_t)f[2] << 8) | f[3]);
  if (f[8] == 0x01 && f[9] == 0x0D) { value = raw / 100.0f; unit = "V"; return true; }
  if (f[8] == 0x01 && f[9] == 0x15) { value = raw / 10.0f; unit = "V"; return true; }
  value = raw; unit = "raw"; return true;
}

void process_bytes() {
  while (len >= 10) {
    bool found = false;
    for (size_t i = 0; i + 1 < len; i++) {
      if (buf[i] == 0xAB && buf[i + 1] == 0xCD) {
        if (i < 6) { memmove(buf, buf + i, len - i); len -= i; return; }
        size_t start = i - 6;
        if (start + 10 > len) return;
        float value; const char *unit;
        if (decode_frame(buf + start, value, unit)) Serial.printf("UT33C+: %.3f %s\n", value, unit);
        size_t consumed = start + 10;
        memmove(buf, buf + consumed, len - consumed);
        len -= consumed;
        found = true;
        break;
      }
    }
    if (!found) { buf[0] = buf[len - 1]; len = 1; }
  }
}

void setup() {
  Serial.begin(115200);
  MeterSerial.begin(2400, SERIAL_8N1, RX_PIN, TX_PIN);
}

void loop() {
  while (MeterSerial.available() && len < sizeof(buf)) buf[len++] = MeterSerial.read();
  process_bytes();
}
```

### MQTT Topics

```text
sensors/ut33cplus/value
sensors/ut33cplus/unit
sensors/ut33cplus/raw_count
sensors/ut33cplus/mode
sensors/ut33cplus/range
```

## Recommended Development Order

1. Validate with the USB serial logger.
2. Capture all ranges and modes.
3. Extend the Python decoder table.
4. Port stable logic to ESP32.
5. Write the sigrok decoder after protocol coverage improves.

## Test Frames

```text
00 00 04 C0 00 D2 AB CD 01 0D -> +12.16 V
FF FF FB 40 03 47 AB CD 01 0D -> -12.16 V
FF FF FF 87 03 9A AB CD 01 15 -> -12.1 V
00 00 01 4C 00 5B AB CD 01 0D -> +3.32 V
```

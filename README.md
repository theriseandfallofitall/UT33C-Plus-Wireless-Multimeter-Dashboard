# UNI-T UT33C+ UART Decode

Tools and protocol documentation for reverse-engineering the hidden UART telemetry stream on UNI-T UT33C+ multimeters.

This project provides a live decoder, guided capture tools, and detailed protocol specifications for the 2400-baud serial stream found inside these meters.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pyserial
```

### 2. Live Decoding
Monitor your multimeter in real-time. Supported modes (DCV, Current, Resistance, etc.) will be automatically decoded.
```bash
python ut33c_plus_logger.py --port COM5
```

### 3. Capture New Data
Use the Session Manager to record raw hex logs for unmapped modes. Logs are automatically saved to the `logs/` directory.
```bash
python ut33c_raw_capture.py
```

---

## 🛠 Project Tools

| Tool | Purpose |
| :--- | :--- |
| `ut33c_plus_logger.py` | **Live Decoder:** Real-time monitoring and CSV logging of confirmed modes. |
| `ut33c_raw_capture.py` | **Session Manager:** Capture raw hex bursts with manual start/stop and labeling. |
| `ut33c_plus_capturer.py`| **Guided Mapper:** Systematic workflow to step through every dial position. |

---

## 📝 Protocol Specification

### Serial Settings
*   **Baud Rate:** 2400
*   **Data Bits:** 8
*   **Parity:** None
*   **Stop Bits:** 1
*   **Update Rate:** ~2 frames per second

### Frame Format
A complete frame is **10 bytes** starting with a fixed sync marker.

```text
AB CD MODE RANGE B0 B1 B2 B3 B4 CS
```

| Byte(s) | Meaning | Status |
|---|---|---|
| `AB CD` | Fixed sync marker | Confirmed |
| `MODE` | Mode identifier (usually `01`) | Confirmed |
| `RANGE` | Function/Range identifier | Confirmed |
| `B0 B1` | Sign extension (usually `00 00` or `FF FF`) | Confirmed |
| `B2 B3` | 16-bit measurement count (**2000-count integer**) | Confirmed |
| `B4` | Sign/Status byte (`00` for Positive, `04` for Negative) | Confirmed |
| `CS` | Checksum | Confirmed |

### Checksum Logic
The checksum is the low byte of the sum of `MODE` through `B4` (Bytes 2 to 8).
```python
checksum = sum(frame[2:9]) & 0xFF
```

---

## 📊 Confirmed Mode Mappings

The UT33C+ is a **2000-count** meter. The values in `B2 B3` represent the discrete steps shown on the LCD.

| Function | Range Byte | Multiplier | Units | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **DC Voltage** | `17` | 0.1 | mV | 0.0 to 199.9 mV |
| **DC Voltage** | `0D` | 0.01 | V | 20V Range |
| **DC Voltage** | `15` | 0.1 | V | 200V Range |
| **Resistance** | `1E` | 1 | Ω | 2000Ω Range |
| **Resistance** | `0E` | 0.01 | kΩ | 20kΩ Range |
| **Resistance** | `1A` | 0.1 | kΩ | 200kΩ Range |
| **Resistance** | `1C` | 0.1 | MΩ | 200MΩ Range |
| **Continuity** | `19` | N/A | status | `0`=Short, `32512`=Open |
| **Diode Test** | `19` | 0.001 | V | V-drop (e.g. 608 = 0.608V) |
| **DC Current** | `1F` | 1 | µA | 2000µA Range |
| **DC Current** | `1B` | 0.01 | mA | 20mA Range |
| **DC Current** | `0F` | 0.1 | mA | 200mA Range |
| **DC Current** | `0B` | 0.01 | A | 10A Range |
| **Temperature**| `16` | 0.1 | °C | UART has 0.1°C resolution |
| **Temperature**| `13` | 0.1 | °F | UART has 0.1°F resolution |

### Overload (OL) & Status
*   **Universal OL:** `7F FF` (32767) in bytes `B2 B3`.
*   **Current OL:** Meter sends a static count of `121` (`0x79`) when a low range is overloaded.
*   **Not Tracked:** APO (Auto Power Off), Hold, and Backlight are local to the LCD and not sent via UART.

---

## ⚠️ Safety Warning

The internal UART ground is typically electrically connected to the meter's common lead. 
*   **DO NOT** connect the meter to a grounded PC while measuring high voltage or mains.
*   **ALWAYS** use an opto-isolated USB adapter or a battery-powered laptop for safe measurements.

---

## 🔍 To Discover
*   [ ] AC Voltage (200V, 600V ranges)
*   [ ] 20MΩ Resistance range
*   [ ] Low Battery status bit detection

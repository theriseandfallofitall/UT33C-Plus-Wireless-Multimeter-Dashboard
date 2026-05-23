# Raspberry Pi Pico 2: Automated Testing Platform
This repository contains a full C++ PlatformIO project to automate the testing of the UT33C+ multimeter.

## Hardware Components
*   **Controller:** Raspberry Pi Pico 2 (RP2350).
*   **Power Control:** N-Channel MOSFET wired to GP16 for low-side power switching.
*   **UART Interfacing:** 
    *   **Serial1 (GP0/GP1):** Connected to Internal High-Speed Pads.
    *   **Serial2 (GP4/GP5):** Connected to External Opto-Port Pads.
*   **Reset Control:** GPIOs for Pad 1 (Soft) and Pad 2 (Hard).

## Software Setup (PlatformIO)
To maintain the high-speed timing required for reset glitching, the project uses the **Earle Philhower RP2040/RP2350 Arduino Core**.

### configuration (`platformio.ini`)
```ini
[env:pico2]
platform = https://github.com/maxgerhardt/platform-raspberrypi.git
board = generic_rp2350
framework = arduino
board_build.core = earlephilhower
monitor_speed = 115200
```

### Build & Upload
1.  Connect Pico 2 in BOOTSEL mode (Hold button while plugging in).
2.  Run `pio run --target upload`.
3.  If upload fails to auto-detect, manually copy `.pio/build/pico2/firmware.uf2` to the RPI-RP2 drive.

## Automation Logic (`src/main.cpp`)
The current firmware performs:
1.  **Heartbeat:** Blinks the onboard LED and prints uptime to the serial monitor.

**NOTE:** The description previously listed advanced fuzzing capabilities. This was inaccurate. The current committed firmware is a simple proof-of-life test. The fuzzing logic described is the **goal**, not the current implementation.

## Serial Output
Logs are sent to your PC at **115200 baud** over USB.
- `INT: ...` indicates data from the high-speed internal pads.
- `EXT: ...` indicates data from the external opto-pads.

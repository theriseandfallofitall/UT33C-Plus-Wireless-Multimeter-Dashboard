# Automated Testing Platform (YD-RP2040)
This repository contains a full C++ PlatformIO project to automate the testing of the UT33C+ multimeter.

## Hardware Components
*   **Controller:** YD-RP2040 (RP2040-based, VCC-GND).
*   **Power Control:** Dual MOSFET setup for full rail isolation.
    *   **GP16 (Positive Rail):** Active HIGH (1=3.3V ON).
    *   **GP17 (GND Rail):** Active LOW (0=GND ON).
*   **UART Interfacing:** 
    *   **Serial1 (GP0/GP1):** Connected to Internal High-Speed Pads.
    *   **Serial2 (GP4/GP5):** Connected to External Opto-Port Pads.
*   **Reset Control:** 
    *   **GP14 (Pad 1):** Soft Reset (Active LOW).
    *   **GP15 (Pad 2):** Hard Reset (Active LOW).

## Software Setup (PlatformIO)
The project uses the **Earle Philhower RP2040/RP2350 Arduino Core** for high-speed GPIO and multi-core timing.

### Configuration (`platformio.ini`)
```ini
[env:pico]
platform = https://github.com/maxgerhardt/platform-raspberrypi.git
board = pico
framework = arduino
board_build.core = earlephilhower
monitor_speed = 115200
```

## Automation Logic (`pico/cpp/src/main.cpp`)
1.  **Inverted Dual-Rail Power Cycle:** Cuts both 3.3V and GND for 1.5s to ensure full capacitor discharge.
2.  **Baud Rate Sweep:** Power cycles and monitors at [2400, 4800, 9600, 19200, 38400, 115200].
3.  **Advanced Fuzzing:** Performs precise timing attacks, NULL blasts, and command injections to unlock hidden MCU states (e.g., State 41).

## Monitoring & Logging
Use `python fuzzer_monitor.py` to capture the fuzzer's serial output and save it to `logs/fuzzer_runs/`.
- `INT: ...` indicates data from the high-speed internal pads.
- `EXT: ...` indicates data from the external opto-pads.

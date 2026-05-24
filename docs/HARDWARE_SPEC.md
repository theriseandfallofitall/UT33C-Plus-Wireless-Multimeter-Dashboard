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

## Chipset Identification (Hypothesis)
Based on the **10-byte frame format** and **2400 baud** rate, the IC is highly likely an **SD7501** (manufactured by SDIC or Jinghua Microelectronics). This chip is the standard for the modern UNI-T "plus" series.

### Key Evidence
1.  **Protocol Match:** The SD7501 uses exactly `AB CD [Mode] [Range] [Flags] [Data High] [Data Mid] [Data Low] [CS High] [CS Low]`.
2.  **State 41 (ASCII 'A'):** In Jinghua/Fortune-style bootloaders, `0x41` is the **"Authorize"** or **"Acknowledge"** response. It indicates the MCU has synchronized with the fuzzer's NULL burst and is waiting for a command prefix.

### Handshake Requirements
Comparative research suggests the MCU expects a **Command Prefix** immediately after responding with `41`.
*   **Candidate 1:** `0xA5` (Common SDIC command start).
*   **Candidate 2:** `0x55` (Sync byte).
*   **Candidate 3:** `0x06` (ACK).

## Automation Logic (`pico/cpp/src/main.cpp`)
1.  **Inverted Dual-Rail Power Cycle:** Cuts both 3.3V and GND for 1.5s to ensure full capacitor discharge.
2.  **Baud Rate Sweep:** Power cycles and monitors at [2400, 4800, 9600, 19200, 38400, 115200].
3.  **Advanced Fuzzing:** Performs precise timing attacks, NULL blasts, and command injections to unlock hidden MCU states (e.g., State 41).

## Monitoring & Logging
Use `python fuzzer_monitor.py` to capture the fuzzer's serial output and save it to `logs/fuzzer_runs/`.
- `INT: ...` indicates data from the high-speed internal pads.
- `EXT: ...` indicates data from the external opto-pads.

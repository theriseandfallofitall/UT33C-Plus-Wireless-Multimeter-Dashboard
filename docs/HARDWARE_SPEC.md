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
The Pico now runs a persistent serial-controlled firmware. It is flashed once, then the PC drives each experiment over USB serial.

1.  **Inverted Dual-Rail Power Cycle:** Cuts both 3.3V and GND for 5.0s (updated from 1.5s) to ensure full capacitor discharge and "True Zero" resets.
2.  **Reusable Rig Primitives:** Exposes power, reset, UART baud, raw transmit, NULL burst, monitor, and marker-response commands.
3.  **Time-Critical Marker Response:** `CYCLE_MARKER` performs the hard power cycle and immediately watches for boot markers (`41`, `FD`, `ED`, `F9`, or other selected bytes) before injecting a response, avoiding host USB latency during the critical window. `RESET_MARKER` performs this same zero-latency watch immediately after pulsing Pad 1 or Pad 2.

## Monitoring & Logging
Use `python pico_rig_runner.py ...` to control and log the rig without reflashing firmware.
- `python pico_rig_runner.py status` checks firmware health.
- `python pico_rig_runner.py monitor --meter-port BOTH --duration-ms 5000` captures raw UART output.
- `python pico_rig_runner.py r34 --attempts 10` reruns the original marker-response experiment.
- For current research, use `python pico_rig_runner.py cmd ...` or focused Python snippets with `PicoRig` to run early-window captures such as the R83 HOLD/SELECT-held external `F9` repeatability test.

Logs are saved to `logs/rig_runs/`.
- `DATA INT ...` indicates data from the high-speed internal pads.
- `DATA EXT ...` indicates data from the external opto-pads.

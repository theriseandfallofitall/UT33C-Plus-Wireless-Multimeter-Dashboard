# Pi Pico Test Rig: Operation Guide

This guide explains how to set up the Raspberry Pi Pico (RP2040/RP2350) rig firmware and run hardware experiments from the host PC without reflashing for every test.

## 1. Environment Setup (PlatformIO)
The test rig uses **PlatformIO** for high-precision timing and multi-core execution.
1. Install **Visual Studio Code**.
2. Install the **PlatformIO IDE** extension.
3. Open the `pico/cpp/` folder in VS Code.

## 2. Building and Deploying
We provide a PowerShell script to automate the build and flash process.
1. Hold the **BOOTSEL** button on your Pico while plugging it into your PC.
2. Run the deployment script from the project root:
   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deploy_pico.ps1
   ```
3. The script will build the UF2 and copy it to the Pico.

## 3. Running Tests Without Reflashing
Once the firmware is deployed, the Pico waits for line-based USB serial commands. Use the host runner for normal experiments:
1. Ensure the Pico is connected to your PC.
2. Check firmware health:
   ```powershell
   python .\pico_rig_runner.py status
   ```
3. Capture both meter UARTs:
   ```powershell
   python .\pico_rig_runner.py monitor --meter-port BOTH --duration-ms 5000
   ```
4. Optionally rerun the original R34 boot-marker response test:
   ```powershell
   python .\pico_rig_runner.py r34 --attempts 10
   ```

Logs are written to `logs/rig_runs/`.

## 4. Discovery Methodology
- **Standard Runs:** The Python runner sequences power, reset, UART transmit, monitor, and marker-response commands.
- **Time-Sensitive Runs:** The Pico firmware provides `CYCLE_MARKER`, which power-cycles the meter and arms marker detection immediately after power-on so the PC cannot miss the boot window.
- **Physical Handshakes:** Some experiments (e.g., R34) require the user to hold the **HOLD/SELECT** button on the meter during the reset window. Follow the runner prompt.

## 5. Analyzing Results
The runner logs raw firmware output from both internal and external pads.
- **Target:** Look for Protocol ID `41` (Gateway) or `FD`/`F9` markers.
- **Goal:** Remote mode control using the `0xA5` command prefix.

## 6. Firmware Command Reference
The runner can send raw commands with `python .\pico_rig_runner.py cmd <command>`. The most useful firmware commands are:

```text
PING
STATUS
POWER ON|OFF|CYCLE [post_ms]
RESET PAD1|PAD2|BOTH [duration_ms]
UART INT|EXT <baud>
TX INT|EXT <hex bytes...>
NULLS INT|EXT <count> [gap_ms]
MONITOR INT|EXT|BOTH <duration_ms>
MARKER INT|EXT <timeout_ms> <post_ms> <markers...> RESP <response...>
CYCLE_MARKER INT|EXT <timeout_ms> <post_ms> <markers...> RESP <response...>
```

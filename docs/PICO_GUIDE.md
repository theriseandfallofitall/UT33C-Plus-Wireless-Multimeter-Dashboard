# Pi Pico Test Rig: Operation Guide

This guide explains how to set up the software environment on your Raspberry Pi Pico (RP2040/RP2350) and run the automated C++ test suite.

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

## 3. Running the Discovery Monitor
Once the firmware is deployed, use the Python monitor to start and log the experiment:
1. Ensure the Pico is connected to your PC.
2. Run:
   ```bash
   python fuzzer_monitor.py
   ```
3. Enter the meter's current mode when prompted.
4. The monitor will send the 'S' (Start) command to the Pico and begin logging the HIL stream to `logs/fuzzer_runs/`.

## 4. Discovery Methodology
- **Standard Runs:** The Pico will autonomously power-cycle and pulse the meter.
- **Physical Handshakes:** Some experiments (e.g., R34) require the user to hold the **SELECT** button on the meter during the reset window. Follow the prompts in the monitor output.

## 5. Analyzing Results
The monitor logs raw hex data from both internal and external pads. 
- **Target:** Look for Protocol ID `41` (Gateway) or `FD`/`F9` markers.
- **Goal:** Remote mode control using the `0xA5` command prefix.

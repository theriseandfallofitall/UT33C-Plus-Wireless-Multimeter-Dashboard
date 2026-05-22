# Pi Pico Test Rig: Operation Guide

This guide explains how to set up the software environment on your Raspberry Pi Pico and run the automated test suite.

## 1. Install MicroPython
1. Download the latest **MicroPython UF2** firmware from [micropython.org](https://micropython.org/download/rp2-pico/).
2. Hold the **BOOTSEL** button on your Pico while plugging it into your PC.
3. Drag and drop the `.uf2` file into the "RPI-RP2" drive.

## 2. Deploy the Script
1. Open your preferred MicroPython editor (e.g., **Thonny** or **VS Code with Pico-W-Go**).
2. Copy the contents of `pico_auto_fuzzer.py` from this repository.
3. Save the file onto the Pico as `main.py`. 
   - *Note: Naming it `main.py` ensures it runs automatically whenever the Pico is powered.*

## 3. Running the Tests
1. Connect all wiring as per `PICO_WIRING.md`.
2. Connect the Pico to your PC via USB.
3. Open a Serial Terminal (Thonny Shell or Putty) to view the live logs.
4. The fuzzer will begin:
   - **Phase 1:** Power cycling the meter at different baud rates.
   - **Phase 2:** Fuzzing the Hard Reset (Pad 2) with various command injections.

## 4. Analyzing Results
The Pico will print logs in the following format:
`[Timestamp] PORT_NAME RECV: <HEX DATA>`

- **If you see text:** It may be a hidden debug console.
- **If you see a change in Byte 3:** You have successfully triggered a remote mode switch!
- **If the meter beeps differently:** You have triggered a hidden diagnostic mode.

## 5. Stopping
To stop the test, simply unplug the Pico or press **Ctrl+C** in your serial terminal.

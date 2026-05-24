# Pi Pico Firmware Guide

This guide explains the two Pico firmware profiles used by the project.

Only one profile should be active as `pico/cpp/src/main.cpp` when building with PlatformIO.

## Firmware Profiles

| Profile | Source | Purpose |
| :--- | :--- | :--- |
| Passive passthrough | `pico/cpp/src/main.cpp` | USB-to-UART bridge for direct logging and on-screen display. Leaves power and reset pins floating. |
| Command rig | `pico/cpp/firmware/main_rig_command.cpp` | Full hardware-in-the-loop rig controller with power, reset, UART monitor, transmit, and marker-response commands. |

## Environment Setup

1. Install Visual Studio Code.
2. Install the PlatformIO IDE extension.
3. Open the `pico/cpp/` folder in VS Code, or build from the repository root with the deployment script.

## Building and Deploying

1. Put the Pico into BOOTSEL mode.
2. Run:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deploy_pico.ps1
   ```

3. The script builds the UF2 and copies it to the mounted Pico drive.

## Using Passive Passthrough Firmware

The passthrough firmware listens to the meter at 2400 baud on `Serial1` and forwards bytes to USB serial at 115200 baud.

Use it with:

```bash
python -m display.big_screen_direct
python -m tools.final_logger
```

This profile is best for normal display and logging because it does not drive the meter power or reset lines.

## Using Command Rig Firmware

To use the automated rig firmware:

1. Copy `pico/cpp/firmware/main_rig_command.cpp` over `pico/cpp/src/main.cpp`.
2. Build and flash with `deploy_pico.ps1`.
3. Control it from the host:

   ```powershell
   python -m tools.pico_rig_runner status
   python -m tools.pico_rig_runner monitor --meter-port BOTH --duration-ms 5000
   python -m tools.pico_rig_runner r34 --attempts 10
   ```

Logs are written to `logs/rig_runs/`.

## Command Rig Reference

The runner can send raw commands with:

```powershell
python -m tools.pico_rig_runner cmd <command>
```

Supported command firmware operations:

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
RESET_MARKER PAD1|PAD2 <duration_ms> INT|EXT <timeout_ms> <post_ms> <markers...> RESP <response...>
```

## Experiment Notes

- The command rig is intended for controlled low-voltage bench experiments only.
- Some tests require manually holding the meter HOLD/SELECT button during the reset window.
- `CYCLE_MARKER` and `RESET_MARKER` keep timing-sensitive marker detection on the Pico to avoid USB round-trip latency.

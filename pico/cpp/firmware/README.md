# Pico Firmware Profiles

This folder stores alternate Pico firmware sources that are not compiled by PlatformIO unless copied into `pico/cpp/src/main.cpp`.

## Available Sources

| File | Purpose |
| :--- | :--- |
| `main_rig_command.cpp` | Serial-controlled hardware-in-the-loop rig firmware. Provides power, reset, UART, monitor, transmit, marker-response, and reset-marker commands. |

## Switching Profiles

The default `pico/cpp/src/main.cpp` is the passive passthrough firmware. To use the command rig:

1. Back up the current `pico/cpp/src/main.cpp` if needed.
2. Copy `pico/cpp/firmware/main_rig_command.cpp` to `pico/cpp/src/main.cpp`.
3. Build and flash with `deploy_pico.ps1`.

Do not place alternate firmware files directly in `pico/cpp/src/`, because PlatformIO will compile every `.cpp` file in that directory.

# Current Status

Active reverse engineering is wrapped up. The project has mapped the passive UART telemetry protocol well enough for reliable logging and display. Remote mode switching was investigated with the Pico rig, but the command path appears to be locked behind an unknown authorization key.

## Repository State

- Decoder and display tools are usable for passive telemetry.
- The shared decoder lives in `ut33c/decoder.py`.
- `display/big_screen_direct.py` is the recommended display for direct 2400 baud capture or Pico passthrough.
- `display/big_screen_rig.py` is for the serial-controlled Pico command rig.
- `pico/cpp/src/main.cpp` currently contains the passive passthrough firmware.
- `pico/cpp/firmware/main_rig_command.cpp` contains the automated command rig firmware.

## Major Discoveries

1. Big-screen display tools were added for live readings, graphing, CSV logging, and snapshots.
2. Missing range bytes were implemented: `0x07` 2000mV DC, `0x11` 600V AC, `0x12` 200V AC, `0x15` 200V DC, and `0x18` 600V DC.
3. The Pico passthrough firmware can act as a passive USB-to-UART adapter without driving power or reset lines.
4. A NULL burst during soft reset can expose protocol ID `41`, interpreted as a gateway or ready state.
5. RX injection was physically verified through reflections on the meter TX line.
6. Entering the diagnostic path requires the physical HOLD/SELECT button during reset.
7. Hard power cycling with dual-rail isolation is the only reliable way to reach the early boot marker window.
8. A 5-second rail-off delay is recommended for repeatable "true zero" resets.
9. The external/opto boot marker depends on dial mode and button state.
10. Exhaustive single-byte, full-frame, and multi-baud probes did not unlock remote mode switching.

## Current Assumptions

- The chipset is an SDIC/Jinghua SD7501-like part.
- Protocol ID `41` is a bootloader or authorization-ready signal.
- The command path probably uses an `0xA5` binary prefix plus an unknown OEM password or key.

## Research Conclusion

The telemetry protocol is usable, but remote mode switching is not currently practical from the known UART pads. Future work would likely require a factory logic analyzer capture, firmware extraction, or fault-injection work instead of more blind UART fuzzing.

## Key Files

| File | Purpose |
| :--- | :--- |
| `ut33c/` | Shared protocol decoder package. |
| `display/` | On-screen display apps plus display config, port discovery, protocol wrapper, dependencies, and launch scripts. |
| `tools/` | Host-side logging, capture, controller, and rig tools. |
| `docs/PROTOCOL_MAP.md` | Frame and range-byte reference. |
| `docs/TESTING_HISTORY.md` | Chronological HIL run history. |
| `docs/PICO_GUIDE.md` | Pico firmware profile guide. |

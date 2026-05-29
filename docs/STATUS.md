# Current Status

Active reverse engineering and hardware discovery are complete. The project has successfully mapped the passive UART telemetry protocol and characterized the various internal pads. While remote mode switching via UART injection remains gated by an unknown authorization sequence, the telemetry stream is fully decoded and usable for high-precision logging and real-time display.

## Repository State

- **Telemetry:** Fully decoded and verified. Decoder lives in `ut33c/decoder.py`.
- **UI:** Real-time on-screen display tools available in `display/`.
- **Firmware:** The Pico C++ Rig Firmware (`pico/cpp/firmware/main_rig_command.cpp`) is the definitive automated controller, supporting high-performance resets, logic probing, and telemetry monitoring.
- **Legacy:** All investigative and "failed" attack scripts have been consolidated into `research/` or `legacy/`.

## Major Discoveries

1. **Big-screen Display:** Live decoded readings, graphing, CSV logging, and snapshot capture are fully implemented.
2. **Protocol Mapping:** All range bytes (DCV, ACV, Resistance, Continuity, Temp) are mapped.
3. **9-Pad Interface:** Confirmed to be the **LCD/Keypad Multiplex Pins**, not a programming header or static mode port. Toggling these pins during operation causes LCD segment interference (all segments lit).
4. **Bootloader Gateway:** ID `41` (Gateway) and `AB FD` (Listener) markers were identified but are extremely time-sensitive and likely require a proprietary OEM key for command execution.
5. **Reset Characteristics:** Hard power cycling (5s discharge) and Soft Reset (Pad 1) are characterized and automated in the rig firmware.

## Current Assumptions

- The chipset is a Jinghua SD7501.
- Remote control of the dial/buttons is only feasible via analog bypass (optocouplers/analog switches) on the 9-pad matrix or mechanical servos.
- Telemetry is the primary and most reliable output path.

## Research Conclusion

The UT33C+ is an excellent, low-cost platform for remote data acquisition via its hidden UART. While the manufacturer has intentionally gated the remote command path, the passive telemetry provides all the data required for high-quality instrumentation.

## Key Files

| File | Purpose |
| :--- | :--- |
| `ut33c/` | Shared protocol decoder package. |
| `display/` | On-screen display apps and real-time UI. |
| `pico/cpp/firmware/` | High-performance C++ Rig and Passthrough firmware. |
| `tools/` | Core logging and rig-running tools. |
| `docs/PROTOCOL_MAP.md` | Final frame and range-byte reference. |
| `docs/HARDWARE_SPEC.md` | Final pad and wiring specification. |


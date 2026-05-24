# Documentation Index

Use this folder as the technical record for the UT33C+ UART reverse-engineering work.

## Start Here

| Document | Purpose |
| :--- | :--- |
| [STATUS.md](STATUS.md) | Current project state, conclusions, and key files. |
| [PROTOCOL_MAP.md](PROTOCOL_MAP.md) | Frame structure, checksum behavior, range bytes, and special states. |
| [PICO_GUIDE.md](PICO_GUIDE.md) | Pico firmware profiles and build/deploy workflow. |
| [PICO_WIRING.md](PICO_WIRING.md) | Bench wiring for the Pico rig. |
| [HARDWARE_SPEC.md](HARDWARE_SPEC.md) | Hardware architecture and rig behavior. |
| [TESTING_HISTORY.md](TESTING_HISTORY.md) | Chronological HIL experiment record. |
| [DISCOVERY_LOG.md](DISCOVERY_LOG.md) | Narrative discovery notes and protocol anomalies. |
| [MODE_CHANGE_PLAN.md](MODE_CHANGE_PLAN.md) | Historical remote-mode-control strategy and final blockers. |
| [Datasheet_and_other_info.md](Datasheet_and_other_info.md) | Datasheet and external reference notes. |
| [AGENTS.md](AGENTS.md) | Repository-specific contributor and agent guidelines. |

## Status Summary

Passive telemetry decoding is usable. Remote mode switching remains locked behind an unknown authorization path and is no longer an active blind-fuzzing target.

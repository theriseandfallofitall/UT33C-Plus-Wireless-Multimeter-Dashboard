# Repository Guidelines

## Project Structure & Module Organization

This repository documents and decodes UART output from the UNI-T UT33C+ multimeter.

- `ut33c/` contains shared protocol decoding code.
- `display/` contains the on-screen display apps plus display config, port discovery, protocol wrapper, dependencies, and launch scripts.
- `tools/` contains host-side logging, capture, controller, and Pico-rig tools.
- `README.md` gives the project overview and research summary.
- `docs/PROTOCOL_MAP.md` records the 10-byte protocol observations and frame details.
- `docs/HARDWARE_SPEC.md` describes the automated rig and HIL integration steps.
- `docs/MODE_CHANGE_PLAN.md` outlines the current strategy for remote control.
- `docs/STATUS.md` tracks current blockers and major discoveries.
- `docs/TESTING_HISTORY.md` provides a chronological log of all HIL fuzzer runs.
- Generated files such as `__pycache__/`, virtual environments, logs, and local `.env` files are ignored.

Keep new source files at the repository root unless the project grows enough to justify a package layout. Put future tests under `tests/`.

## Build, Test, and Development Commands

Create an isolated environment before installing dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pyserial
```

Or install the repo dependency set:

```powershell
pip install -r requirements.txt
```

Run the logger against a Windows serial port:

```powershell
python -m tools.final_logger
```

The logger writes a timestamped CSV under `logs/` automatically:

```powershell
python -m tools.final_logger
```

Run the decoder regression tests:

```powershell
python -m unittest tests.test_decoder
```

Check that the main Python tools compile:

```powershell
python -m py_compile .\ut33c/decoder.py .\tools/final_logger.py .\tools/pico_rig_runner.py
```

Build the Pico firmware:

```powershell
pio run -d .\pico\cpp
```

Monitor both meter UARTs through the Pico rig:

```powershell
python -m tools.pico_rig_runner monitor --meter-port BOTH --duration-ms 5000
```

## Coding Style & Naming Conventions

Use Python 3 with type hints where they clarify data shape. Keep protocol helpers small and deterministic, as in `checksum_ok`, `decode_frame`, and `pop_next_frame`. Prefer `snake_case` for functions and variables, `PascalCase` for dataclasses, and uppercase hex literals such as `0xAB`.

When changing decoder behavior, preserve existing CLI flags unless there is a clear compatibility reason. Keep serial settings explicit: baud, bytesize, parity, stopbits, and timeout.

## Testing Guidelines

Decoder regression tests live in `tests/test_decoder.py` and use curated capture logs from `logs/`. For decoder changes, add focused tests under `tests/test_*.py` using captured frame bytes from the protocol notes. Cover checksum rejection, marker alignment, signed conversion, known voltage ranges, and unknown valid ranges.

Before shipping decoder or firmware changes, run `python -m unittest tests.test_decoder`, `python -m py_compile .\ut33c/decoder.py .\tools/final_logger.py .\tools/pico_rig_runner.py`, `pio run -d .\pico\cpp`, and manually validate with a real or recorded serial stream when hardware is available.

## Commit & Pull Request Guidelines

The current history uses a short, descriptive commit subject, for example `Initial UT33C Plus UART decode notes`. Continue using imperative, concise subjects such as `Add CSV decoding test cases` or `Document resistance mode frames`.

Pull requests should include a brief summary, any hardware used for validation, sample frames or CSV output when behavior changes, and links to related findings. Include screenshots only when documenting terminal output or external tool setup.

## Security & Configuration Tips

Do not commit `.env`, virtual environments, raw logs with sensitive host paths, or large capture files unless they are intentionally curated fixtures. Prefer small anonymized frame samples in docs or tests.

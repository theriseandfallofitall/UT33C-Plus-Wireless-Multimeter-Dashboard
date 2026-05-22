# Repository Guidelines

## Project Structure & Module Organization

This repository documents and decodes UART output from the UNI-T UT33C+ multimeter.

- `ut33c_plus_logger.py` contains the serial reader, frame finder, checksum validation, decoder, CLI, and optional CSV logging.
- `README.md` gives the short project overview.
- `UT33C_PLUS_UART_PROTOCOL_FINDINGS.md` records protocol observations and frame details.
- `UT33C_PLUS_INTEGRATION_STEPS.md` describes hardware and integration steps.
- Generated files such as `__pycache__/`, virtual environments, logs, and local `.env` files are ignored.

Keep new source files at the repository root unless the project grows enough to justify a package layout. Put future tests under `tests/`.

## Build, Test, and Development Commands

Create an isolated environment before installing dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pyserial
```

Run the logger against a Windows serial port:

```powershell
python .\ut33c_plus_logger.py --port COM5
```

Run with CSV output:

```powershell
python .\ut33c_plus_logger.py --port COM5 --csv readings.csv
```

Check that the script compiles:

```powershell
python -m py_compile .\ut33c_plus_logger.py
```

## Coding Style & Naming Conventions

Use Python 3 with type hints where they clarify data shape. Keep protocol helpers small and deterministic, as in `checksum_ok`, `decode_frame`, and `find_frames`. Prefer `snake_case` for functions and variables, `PascalCase` for dataclasses, and uppercase hex literals such as `0xAB`.

When changing decoder behavior, preserve existing CLI flags unless there is a clear compatibility reason. Keep serial settings explicit: baud, bytesize, parity, stopbits, and timeout.

## Testing Guidelines

No automated test suite is committed yet. For decoder changes, add focused tests under `tests/test_*.py` using captured frame bytes from the protocol notes. Cover checksum rejection, marker alignment, signed 16-bit conversion, known voltage ranges, and unknown valid ranges.

Until tests exist, run `python -m py_compile .\ut33c_plus_logger.py` and manually validate with a real or recorded serial stream.

## Commit & Pull Request Guidelines

The current history uses a short, descriptive commit subject, for example `Initial UT33C Plus UART decode notes`. Continue using imperative, concise subjects such as `Add CSV decoding test cases` or `Document resistance mode frames`.

Pull requests should include a brief summary, any hardware used for validation, sample frames or CSV output when behavior changes, and links to related findings. Include screenshots only when documenting terminal output or external tool setup.

## Security & Configuration Tips

Do not commit `.env`, virtual environments, raw logs with sensitive host paths, or large capture files unless they are intentionally curated fixtures. Prefer small anonymized frame samples in docs or tests.

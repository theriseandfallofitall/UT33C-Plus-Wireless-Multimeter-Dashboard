# Display Applications

This folder contains the on-screen display workflow for decoded UT33C+ telemetry.

## Files

| File | Purpose |
| :--- | :--- |
| `big_screen_direct.py` | Display app for a direct 2400 baud UART stream from USB-serial or Pico passthrough firmware. |
| `big_screen_rig.py` | Display app for the serial-controlled Pico command rig. Sends `MONITOR INT` and decodes returned `DATA` lines. |
| `config.py` | Display log paths, snapshot file name, Pico USB baud, and Pico monitor command. |
| `ports.py` | Serial-port discovery helper used by both display apps. |
| `protocol.py` | Display-facing protocol import layer for frame decoding. |
| `requirements.txt` | Display-specific Python dependencies. |
| `run_direct.ps1` | PowerShell launcher for the direct display. |
| `run_rig.ps1` | PowerShell launcher for the Pico-rig display. |

## Setup

From the repository root:

```bash
pip install -r display/requirements.txt
```

`tkinter` is included with most Python distributions. If Python was installed without Tk support, install a Python build that includes Tk.

## Run

From the repository root:

```bash
python -m display.big_screen_direct
python -m display.big_screen_rig
```

On Windows, the launch scripts can also be run directly:

```powershell
.\display\run_direct.ps1
.\display\run_rig.ps1
```

Display logs and snapshots are written to the repository-level `logs/` folder.

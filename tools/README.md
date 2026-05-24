# Host Tools

Operational scripts for normal logging, raw capture, experimental serial control, and Pico rig automation.

| File | Purpose |
| :--- | :--- |
| `final_logger.py` | Console decoder and CSV logger for direct telemetry. |
| `raw_capture.py` | Manual raw capture tool for building small fixture logs. |
| `experimental_controller.py` | Historical command sender for testing candidate control bytes. |
| `fuzzer_monitor.py` | Stream logger for earlier Pico fuzzer workflows. |
| `pico_rig_runner.py` | Main host controller for the serial-command Pico rig. |

Run from the repository root with module syntax:

```bash
python -m tools.final_logger
python -m tools.raw_capture --help
python -m tools.pico_rig_runner --help
```

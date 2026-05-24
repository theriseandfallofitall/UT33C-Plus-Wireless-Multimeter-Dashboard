# Datasheet and Reference Notes

This file is reserved for curated datasheet links, chipset notes, and external protocol references.

Current working hypothesis:
- The UT33C+ protocol is consistent with an SDIC/Jinghua SD7501-like chipset.
- The meter emits 10-byte `AB CD` frames at 2400 baud.
- Confirmed project findings and run evidence live in `docs/PROTOCOL_MAP.md`, `docs/DISCOVERY_LOG.md`, and `docs/TESTING_HISTORY.md`.

Do not treat external datasheet assumptions as confirmed unless they are backed by a local HIL run or captured frame in this repository.

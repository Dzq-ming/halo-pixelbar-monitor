# Contributing

1. Use Python 3.11 or newer.
2. Run `python -m unittest discover -s tests -v`.
3. Stage only intended source/documentation files and run
   `python scripts/check_public_files.py`.
4. Explain whether a change was tested with a fake device or real hardware.

The only tested speaker edition is **Halo PixelBar 2026 upgraded edition**,
USB product ID `A160`. For another revision, provide a sanitized compatibility
report before expanding the HID allowlist. Include edition, VID/PID, interface,
usage page, ASCII capacity and whether text restoration works. Do not include
serial numbers, raw device paths, personal screen text or complete runtime logs.

Keep the dashboard's 32 ASCII cells and fixed separator positions covered by
tests. Test missing readings, transitions to 100%, corrupted replies and readback
mismatches. Do not add unverified firmware, reset or arbitrary raw-packet commands.

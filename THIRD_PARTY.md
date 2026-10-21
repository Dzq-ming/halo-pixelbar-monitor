# Third-party software and protocol references

This is an independent community project. It is not affiliated with or endorsed
by EDIFIER. No official SDK or public drawing-protocol specification is claimed.

| Component | Purpose | License / source |
| --- | --- | --- |
| hidapi Python package 0.15.0 | Local USB HID transport | [Project and licenses](https://github.com/trezor/cython-hidapi) |
| LibreHardwareMonitor 0.9.6 | Numeric temperature/load sensors | [MPL-2.0 and upstream component notices](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) |
| PawnIO signed edition | Privileged CPU sensor access | [Official distributions and terms](https://pawnio.eu/) |
| halo-pixelbar-mcp | Community reference for HID framing, text, color and layouts | [MIT](https://github.com/Seraph310/halo-pixelbar-mcp) |
| HaloPixelToolBox | Community reference for EC-family text/layout framing | [MIT](https://github.com/XFEstudio/HaloPixelToolBox) |

The monitor's transport is adapted from the protocol observations in these
community references and validated for the tested A160 interface. Corresponding
MIT notices are preserved in `docs/licenses/`.

Downloaded applications, libraries, drivers and their assets are not included
in this repository. `Setup.ps1` fetches the complete LibreHardwareMonitor release,
preserving the upstream archive's component files, and verifies SHA-256 hashes.
PawnIO is separately downloaded from a pinned upstream commit and its Authenticode
signature is checked before installation. Those components retain their own terms.

No extracted official application code, decompiled output, vendor firmware,
official application installer, account material or captured personal screen text
is distributed here. Public documentation links and independently implemented
bounded text commands are used instead.

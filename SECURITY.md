# Security and privacy

The running monitor communicates with a locally connected USB speaker and local
hardware sensors. It has no telemetry, account login, HTTP listener, remote
control server, network-speed collector or runtime upload feature.

Installation accesses Python package services and official upstream download
hosts. Dependency archives and the driver installer are hash checked; the driver
signature is checked again before installation. Administrator rights are needed
for some CPU sensors and for the first PawnIO installation.

All runtime data stays under `runtime/`, which is ignored by Git. This includes
numeric sensor readings, process IDs, logs, and a snapshot of the screen before
monitoring. **The screen snapshot may contain your own custom text. Do not attach
the runtime folder to an issue.** The monitor does not save device serials, raw
USB instance paths, computer names or network adapter names. Logs record error
classes rather than full exception messages or stack traces.

`config.json`, `.venv/`, `lib/`, downloaded binaries, logs, state snapshots and
research outputs are excluded from publication. The public-file check is useful
but is not a guarantee that arbitrary future changes contain no private data.

Before publishing a diagnostic report, remove account information, device serials,
custom screen text, local user paths and unrelated system details. Use GitHub's
private vulnerability reporting if available; do not put credentials in public
issues. This software does not modify firmware, fan settings or speaker volume.

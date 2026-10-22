# Changelog

## 0.1.1

- Fix Windows sensor snapshot replacement failures stopping the monitor.
  Atomic replacement with bounded retries preserves the last good sample;
  persistent contention skips a sample instead of terminating the worker.
- Retain recent readings during temporary read conflicts, expire them after
  10 seconds, and keep diagnostic file locks from interrupting the display.
- Add regression checks for Windows file locks and recovery.

## 0.1.0

- Initial Windows monitor for Halo PixelBar **2026 upgraded edition** (`A160`).
- Fixed 32-character centered dashboard for CPU/GPU temperature and load,
  memory use, and 24-hour time.
- Bounded text protocol, checksum validation, text readback, reconnection,
  stale-data placeholders and previous-screen restoration.
- Portable setup with verified downloads, local-only runtime data,
  public-file checks and Windows CI.

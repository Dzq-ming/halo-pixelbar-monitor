"""Display worker. Start through Start-Monitor.cmd for live sensor data."""
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import time

from .config import DEFAULTS, read_config
from .formatting import dashboard
from .protocol import Screen

ROOT = Path(__file__).resolve().parent.parent


def atomic_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description="Halo PixelBar 2026 upgraded edition performance display")
    parser.add_argument("--preview", action="store_true", help="Print synthetic sample; no device access")
    args = parser.parse_args()
    if args.preview:
        print(dashboard({"cpu_temp":42, "cpu_load":8, "gpu_temp":45, "gpu_load":12, "memory_load":67}))
        return 0
    if sys.platform != "win32":
        parser.error("Live device mode requires Windows")
    import msvcrt
    runtime = ROOT / "runtime"
    runtime.mkdir(exist_ok=True)
    handler = RotatingFileHandler(runtime / "display.log", maxBytes=128*1024, backupCount=2, encoding="utf8")
    logging.basicConfig(handlers=[handler], level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    lock = (runtime / "display.lock").open("a+b")
    lock.seek(0)
    try:
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        lock.close()
        return 0
    screen = None
    snapshot = None
    config = DEFAULTS.copy()
    last_error = None
    try:
        while not (runtime / "stop.flag").exists():
            try:
                config = read_config(ROOT / "config.json")
            except (OSError, ValueError):
                logging.warning("Invalid configuration; retaining last valid settings")
            try:
                try:
                    data = json.loads((runtime / "sensors.json").read_text(encoding="utf-8-sig"))
                except (OSError, ValueError):
                    data = {}
                stamp = data.get("timestamp")
                if type(stamp) not in (int,float) or not 0 <= time.time()-stamp <= 10:
                    data = {}
                text = dashboard(data, offset_hours=config["timezone_offset_hours"])
                if screen is None:
                    screen = Screen()
                    if snapshot is None:
                        # Snapshot before the first write, never overwrite it on reconnect.
                        snapshot = screen.snapshot()
                        atomic_json(runtime / "previous-screen.json", snapshot)
                hot = ((data.get("cpu_temp") or 0) >= config["hot_cpu_c"]
                       or (data.get("gpu_temp") or 0) >= config["hot_gpu_c"])
                screen.show(text, (255,120,40) if hot else (102,200,255), config["alignment"])
                atomic_json(runtime / "display-status.json", {"timestamp":time.time(), "text":text, "verified":True})
                if last_error:
                    logging.info("Screen reconnected and text verified")
                last_error = None
            except Exception as exc:
                # Avoid logging raw HID exceptions: they may include USB paths or serials.
                error = type(exc).__name__
                if error != last_error:
                    logging.error("Display update failed (%s); retrying", error)
                last_error = error
                if screen:
                    screen.close()
                    screen = None
                atomic_json(runtime / "display-status.json", {"timestamp":time.time(), "verified":False, "error":error})
            deadline = time.monotonic() + config["refresh_seconds"]
            while time.monotonic() < deadline and not (runtime / "stop.flag").exists():
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if config["restore_on_exit"] and snapshot:
            try:
                if screen is None:
                    screen = Screen()
                screen.restore(snapshot)
            except Exception as exc:
                logging.warning("Previous screen could not be restored (%s)", type(exc).__name__)
        if screen:
            screen.close()
        lock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

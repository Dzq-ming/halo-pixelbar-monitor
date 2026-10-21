"""Portable settings; no personal paths or device identity are required."""
import json
import math
from pathlib import Path

DEFAULTS = {
    "alignment": "center", "refresh_seconds": 2.0,
    "timezone_offset_hours": 8, "hot_cpu_c": 85, "hot_gpu_c": 80,
    "gpu_index": 0, "restore_on_exit": True,
}


def read_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    if not isinstance(data, dict) or set(data) - set(DEFAULTS):
        raise ValueError("Unknown configuration keys")
    result = DEFAULTS | data
    if result["alignment"] not in ("left", "center", "right", "stretch"):
        raise ValueError("Invalid alignment")
    ranges = {"refresh_seconds": (1, 60), "timezone_offset_hours": (-12, 14),
              "hot_cpu_c": (1, 150), "hot_gpu_c": (1, 150)}
    for key, (low, high) in ranges.items():
        value = result[key]
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("Invalid numeric setting")
    if type(result["gpu_index"]) is not int or result["gpu_index"] < 0:
        raise ValueError("Invalid GPU index")
    if type(result["restore_on_exit"]) is not bool:
        raise ValueError("Invalid restore setting")
    return result

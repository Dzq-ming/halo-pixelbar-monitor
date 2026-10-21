"""Fixed display columns, independent from USB and sensor access."""
from datetime import datetime, timedelta, timezone
import math


def number(value, maximum=999):
    if type(value) not in (int, float) or not math.isfinite(value):
        return "--"
    rounded = round(value)
    return f"{rounded:>2}" if 0 <= rounded <= maximum else "--"


def dashboard(data, now=None, offset_hours=8):
    now = now or datetime.now(timezone(timedelta(hours=offset_hours)))
    cpu = f"C{number(data.get('cpu_temp'))}/{number(data.get('cpu_load'), 100)}"
    gpu = f"G{number(data.get('gpu_temp'))}/{number(data.get('gpu_load'), 100)}"
    memory = f"M{number(data.get('memory_load'), 100)}"
    text = f" {cpu:<8}| {gpu:<8}| {memory:<4}| {now:%H:%M}"
    if len(text) != 32 or not text.isascii():
        raise ValueError("Unexpected display width")
    return text

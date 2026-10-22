"""Local JSON exchange resilient to short Windows file sharing conflicts."""
import json
import os
import time


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    content = json.dumps(value, ensure_ascii=False, indent=2)
    for attempt in range(10):
        try:
            temporary.write_text(content, encoding='utf8')
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(0.025)


def read_sensors(path, previous=None, now=None):
    """Retain a recent sample during contention, never display stale readings."""
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            data = previous or {}
    except (OSError, ValueError):
        data = previous or {}
    stamp = data.get('timestamp')
    now = time.time() if now is None else now
    if type(stamp) not in (int, float) or not 0 <= now - stamp <= 10:
        return {}
    return data

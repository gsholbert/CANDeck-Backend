import time
from pathlib import Path
import yaml
import json
from typing import Dict, Any
from core.constants import Paths

last_updated_values = {}

def should_update(signal, value, interval=0.25):
    now = time.time()
    last_value, last_time = last_updated_values.get(signal, (None, 0))
    if value != last_value or now - last_time > interval:
        last_updated_values[signal] = (value, now)
        return True
    return False

def write_snapshot(update: Dict[str, Any], file_path: Path = Paths.SNAPSHOT_FILE):
    existing = {}

    if file_path.exists():
        try:
            with file_path.open("w") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            print("[WARN] Corrupt snapshot file -- Overwriting")

    existing.update(update)

    with file_path.open("w") as f:
        json.dump(existing, f, indent=2)
    print("Snapshot Saved!")
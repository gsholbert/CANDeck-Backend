import time
from pathlib import Path
import yaml
import json
from typing import Dict, Any

last_updated_values = {}
SNAPSHOT_FILE = Path("snapshot.json")

def should_update(signal, value, interval=0.25):
    now = time.time()
    last_value, last_time = last_updated_values.get(signal, (None, 0))
    if value != last_value or now - last_time > interval:
        last_updated_values[signal] = (value, now)
        return True
    return False

def write_snapshot(update: dict, file_path: str = "snapshot.json"):
    existing = {}

    if Path(file_path).exists():
        try:
            with open(file_path, "r") as f:
                existing = json.load(f)
        except json.JSONDecodError:
            print("[WARN] Corrupt snapshot file -- Overwriting")

    existing.update(update)

    with open(file_path, "w") as f:
        json.dump(existing, f, indent=2)
    print("Snapshot Saved!")

def load_config_and_schema(config_path: Path, schema_dir: Path) -> Dict[str, Any]:
    #load config.yaml
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    ecu = config.get("ecu")
    if not ecu:
        raise ValueError("Missing 'ecu' field in config.yaml")
    
    schema_path = schema_dir / f"{ecu}.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema for ECU '{ecu}' not found at {schema_path}")
    
    with open(schema_path, "r") as f:
        schema = json.load(f)

    return {
        "config": config,
        "schema": schema
    }
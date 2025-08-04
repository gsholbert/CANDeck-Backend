from pathlib import Path
import yaml
import json
from typing import Dict, Any

def load_config_and_schema(config_path: Path, schema_dir: Path) -> Dict[str, Any]:
    #load config.yaml
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    ecu = config.get("ecu", {}).get("brand", {})
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
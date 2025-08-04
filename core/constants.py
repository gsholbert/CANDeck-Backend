# constants.py

from pathlib import Path
from core.bootstrap import load_config_and_schema

class Paths:
    SNAPSHOT_FILE = Path("snapshot.json")

class Defaults:
    CAN_CHANNEL = "canVirtual"
    WEBSOCKET_HOST = "localhost"
    WEBSOCKET_PORT = 8765

class Timing:
    BUS_DECAY_INTERVAL = 5
    MIN_DECAY_INTERVAL = 1
    SNAPSHOT_INTERVAL = 0.25

class Config:
    paths = load_config_and_schema(Path("config.yaml"), Path("schemas"))
    data = paths["config"]
    schema = paths["schema"]

class State:
    active_signals = set()
    last_values = {}
from utils.utils import load_config_and_schema
from pathlib import Path

paths = load_config_and_schema(Path("config.yaml"), Path("schemas"))
config = paths["config"]
active_signals = set()
signal_schema = paths["schema"]
last_values = {}
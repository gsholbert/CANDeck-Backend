# =============================
# transport/__init__.py
# =============================

# Public interface for the transport module.
# This module is responsible for CAN bus management, including message sending/receiving,
# dynamic bus control (start/stop), and access to signal definitions.

from pathlib import Path
from utils.utils import load_config_and_schema
from .bus_manager import BusManager

paths = load_config_and_schema(Path("config.yaml"), Path("schemas"))
config = paths["config"]
signal_schema = paths["schema"]
active_signals = set()
last_values = {}

bus_manager = BusManager(config=config)

__all__ = [
    "config",
    "signal_schema",
    "active_signals",
    "last_values",
    "bus_manager"
]
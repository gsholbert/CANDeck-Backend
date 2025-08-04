import os
import importlib
import pathlib

# Internal registry of handlers
handler_map = {}

# Get the directory path of this file
base_path = pathlib.Path(__file__).parent

# Dynamically load all Python modules in this directory (except __init__.py and private files)
for file in sorted(base_path.glob("*.py")):
    if file.name.startswith("_") or file.name == "__init__.py":
        continue

    module_name = f"{__name__}.{file.stem}"  # e.g., routes.handlers.streamdeck
    try:
        module = importlib.import_module(module_name)

        # Convention: Each handler file must expose a 'register' function
        if hasattr(module, "register"):
            module.register(handler_map)
    except Exception as e:
        print(f"[ERROR] Failed to import handler module {module_name}: {e}")

# Public interface
__all__ = ["handler_map"]

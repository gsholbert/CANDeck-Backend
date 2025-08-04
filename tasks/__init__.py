# =============================
# tasks/__init__.py
# =============================

# Dynamically loads all task modules and gathers any long-running coroutines they expose.
# Each module must define either `get_task()` (single) or `get_tasks()` (multiple).

import pathlib
import importlib
import asyncio

__all__ = ["get_all_tasks"]

async def get_all_tasks():
    """
    Scans the tasks directory and collects all coroutine-producing functions
    (`get_task()` or `get_tasks()`) from each Python file.
    """
    tasks = []

    base_path = pathlib.Path(__file__).parent
    for file in base_path.glob("*.py"):
        if file.name.startswith("_") or file.name == "__init__.py":
            continue

        module_name = f"{__name__}.{file.stem}"
        try:
            module = importlib.import_module(module_name)
            print(f"[DEBUG] Successfully imported {module_name}")

            if hasattr(module, "get_tasks") and callable(module.get_tasks):
                print(f"[DEBUG] Gathering tasks for module {module_name}")
                result = await module.get_tasks()
                if isinstance(result, list):
                    for task in result:
                        if not isinstance(task, asyncio.Task):
                            print(f"[ERROR] Task in {module_name} is not an asyncio.Task: {task}")
                    tasks.extend(result)
                    print(f"[DEBUG] Successfully added tasks for module {module_name}")
                else:
                    raise TypeError(f"{module_name}.get_tasks() must return a list")
            else:
                raise AttributeError(f"{module_name} must define async get_tasks() returning List[asyncio.Task]")
        except Exception as e:
            print(f"[ERROR] Loading task from {module_name}: {e}")

    return tasks

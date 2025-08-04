# main.py

import asyncio
import signal

from core.constants import *
from core.bootstrap import *
from core.app_contexts import *

from tasks import get_all_tasks
from utils.shutdown import shutdown
from transport.bus_manager import BusManager
from transport.server_manager import ServerManager

Managers.bus_manager = BusManager(Config.data)
Managers.server_manager = ServerManager(Config.data)

# Track running tasks to cancel on exit
running_tasks = []

def handle_shutdown():
    print("[MAIN] Caught shutdown signal, cancelling all tasks...")
    for task in running_tasks:
        task.cancel()

async def main():
    print("[DEBUG] starting program")
    global running_tasks

    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, handle_shutdown)
    loop.add_signal_handler(signal.SIGTERM, handle_shutdown)
    print("[DEBUG] Added shutdown signals")

    try:
        print("[DEBUG] Adding tasks")
        # Dynamically gather all tasks
        tasks = await get_all_tasks()
        running_tasks = tasks  # Save for later cancellation

        print("[DEBUG] Tasks retrieved")

        # Wait for all tasks (usually long-lived)
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("[MAIN] Tasks cancelled. Beginning graceful shutdown.")
    finally:
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())

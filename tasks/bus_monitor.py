import asyncio
from typing import Dict
from core.constants import Timing
from core.app_contexts import Managers
from transport.canbus_interface import start_can_monitor
from transport.bus_manager import BusStatus

class BusMonitor:
    def __init__(self, bus_manager=Managers.bus_manager, interval=Timing.BUS_DECAY_INTERVAL):
        self.bus_manager = bus_manager
        # Store active monitor tasks by channel name
        self._bus_decay_tasks: Dict[str, asyncio.Task] = {}
        self._decay_watchlist = []

        # How often (in seconds) we check bus usage
        self.DECAY_INTERVAL = max(interval, Timing.MIN_DECAY_INTERVAL)
        
        self.status_handler = {
            BusStatus.ACTIVE: lambda channel: None,
            BusStatus.SHUTDOWN: lambda channel: self._bus_decay_tasks.pop(channel, None),
            BusStatus.NOT_FOUND: lambda channel: (
                self._bus_decay_tasks.pop(channel, None),
                print(f"[WARN] Mismatch found between task and bus lists for {channel}")),
            BusStatus.PERMANENT: lambda channel: (
                self._bus_decay_tasks.pop(channel),
                print(f"[ERROR] Dynamic task created for permanent bus {channel}"))
        }

    async def monitor_loop(self):
        while True:
            self._decay_watchlist = [
                name for name in self.bus_manager._buses.keys()
                if self.bus_manager._bus_lifecycles.get(name, "dynamic") == "dynamic"
            ]

            await asyncio.sleep(self.DECAY_INTERVAL)

            for channel in self._decay_watchlist:
                await self._monitor_bus(channel)

    async def _monitor_bus(self, channel: str):
        """
        Periodically calls release_bus on the given channel.
        Terminates when bus usage hits 0 or below.
        """
        try:
            while True:
                status = await self.bus_manager.release_bus(channel)

                if channel not in self._bus_decay_tasks:
                    print(f"[WARN] {channel} not found in task list; exiting")
                    return

                handler = self.status_handler.get(status)
                if handler:
                    handler(channel)

                if status in (BusStatus.SHUTDOWN, BusStatus.NOT_FOUND, BusStatus.PERMANENT):
                    break
        except asyncio.CancelledError:
            print(f"[DECAY] Bus monitor for '{channel}' cancelled.")
            self._bus_decay_tasks.pop(channel, None)

    async def track_bus(self, channel: str):
        """
        Starts a background decay task for a new channel if one doesn't already exist.
        """
        if channel not in self._bus_decay_tasks:
            await self.bus_manager.get_bus(channel)
            print(f"[bus_monitor] Starting decay monitor for bus '{channel}'")
            task = asyncio.create_task(self._monitor_bus(channel))
            self._bus_decay_tasks[channel] = task


bus_monitor = BusMonitor()
_task_cache = []

async def get_tasks():
    if _task_cache:
        return _task_cache

    _task_cache.extend([
        asyncio.create_task(bus_monitor.monitor_loop())
    ])
    return _task_cache
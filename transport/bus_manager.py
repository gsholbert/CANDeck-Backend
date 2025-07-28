# transport/bus_manager.py

import asyncio
from typing import Dict
import can

class BusManager:
    """
    Manages creation, reuse, and cleanup of CAN bus interfaces.
    """

    def __init__(self, config: dict):
        self.config = config
        self._buses: Dict[str, can.Bus] = {}
        self._usage_counts: Dict[str, int] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def get_bus(self, channel_name: str) -> can.Bus:
        """
        Returns an active bus for the given channel, creating it if needed.
        Increments the usage count.
        """
        if channel_name not in self._buses:
            self._buses[channel_name] = self._create_can_bus(channel_name)
            self._usage_counts[channel_name] = 0
            self._locks[channel_name] = asyncio.Lock()
        self._usage_counts[channel_name] += 1
        return self._buses[channel_name]

    async def release_bus(self, channel_name: str):
        """
        Decrements the usage count and shuts down the bus if no more users remain.
        """
        if channel_name not in self._usage_counts:
            return
        self._usage_counts[channel_name] -= 1
        if self._usage_counts[channel_name] <= 0:
            bus = self._buses.pop(channel_name, None)
            if bus:
                bus.shutdown()
            self._usage_counts.pop(channel_name)
            self._locks.pop(channel_name)

    def get_lock(self, channel_name: str) -> asyncio.Lock:
        """
        Returns the asyncio lock associated with this channel to coordinate access.
        """
        return self._locks.get(channel_name, asyncio.Lock())

    def _create_can_bus(self, channel_name: str) -> can.Bus:
        """
        Internal method to create a new can.Bus instance based on config.
        """
        buscfg = self.config.get("can_interfaces", {}).get(channel_name, {})

        interface = buscfg.get("interface", "socketcan")
        channel = buscfg.get("channel", "can0")
        bitrate = buscfg.get("bitrate", "500000")
        receive_own_messages = buscfg.get("receive_own_messages", False)

        return can.Bus(
            interface=interface,
            channel=channel,
            bitrate=bitrate,
            receive_own_messages=receive_own_messages
        )
    
    async def shutdown_all_buses(self) -> bool:
        """
        Gracefully shuts down all active CAN buses and clears internal state.
        Returns True if successful, False otherwise.
        """
        try:
            for channel in list(self._buses.keys()):
                bus = self._buses.pop(channel, None)
                if bus:
                    bus.shutdown()
                self._usage_counts.pop(channel, None)
                self._locks.pop(channel, None)

            return not self._buses and not self._usage_counts and not self._locks

        except Exception as e:
            print(f"Error during bus shutdown: {e}")
            return False
        
    def is_active(self, channel: str) -> bool:
     return channel in self._buses

    def list_active_channels(self) -> list[str]:
        return list(self._buses.keys())

    def force_shutdown(self, channel: str):
        bus = self._buses.pop(channel, None)
        if bus:
            bus.shutdown()
        self._usage_counts.pop(channel, None)
        self._locks.pop(channel, None)

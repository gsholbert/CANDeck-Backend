import asyncio
from transport.canbus_interface import start_can_monitor

async def get_tasks():
    return [asyncio.create_task(start_can_monitor())]
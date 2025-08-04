import asyncio
from core.app_contexts import Managers

async def get_tasks():
    # servers = await Managers.server_manager.start_all_servers()
    return [asyncio.create_task(Managers.server_manager.start_all_servers())]
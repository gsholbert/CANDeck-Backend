import asyncio
from core.app_contexts import Managers

async def shutdown():
    print("Beginning Shutdown process...")

    try:
        await Managers.server_manager.shutdown_all_servers()
        print("[SHUTDOWN] All web servers shut down")
    except Exception as e:
        print(f"[ERROR] Error shutting down websockets: {e}")

    try:
        await Managers.bus_manager.shutdown_all_buses()
        print("[SHUTDOWN] All buses shut down")
    except Exception as e:
        print(f"[ERROR] Error shutting down buses: {e}")
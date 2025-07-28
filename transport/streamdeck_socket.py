# transport/server_manager.py

import asyncio
import websockets
import json
from typing import Dict, Callable, Awaitable, Optional
from routes.router import dispatch


class ServerManager:
    """
    Manages creation and handling of WebSocket servers for accessories/HIDs.
    Each server runs on a host/port and dispatches messages to a shared or per-server dispatcher.
    """

    def __init__(self, config: Dict, dispatch_fn: Optional[Callable[[Dict], Awaitable[Dict]]] = None):
        self._config = config.get("websocket_interfaces", {})
        self._servers = {}
        self._locks = {}
        self._dispatch_fn = dispatch_fn or dispatch

    async def _handle_connection(self, websocket, path: str):
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"Message Received on {path}: {data}")
                response = await self._dispatch_fn(data)
                if response:
                    await websocket.send(json.dumps(response))
        except Exception as e:
            print(f"WebSocket error on {path}: {e}")

    async def _start_single_server(self, name: str, host: str, port: int):
        print(f"Starting WebSocket server '{name}' on ws://{host}:{port}")

        async def handler(websocket, path):
            await self._handle_connection(websocket, path)

        server = await websockets.serve(handler, host, port)
        self._servers[name] = server
        self._locks[name] = asyncio.Lock()

    async def start_all_servers(self):
        """
        Starts all servers defined in the config under `websocket_interfaces`.
        """
        for name, settings in self._config.items():
            host = settings.get("host", "localhost")
            port = settings.get("port", 8765)
            await self._start_single_server(name, host, port)

    async def shutdown_single_server(self, channel_name):
        if channel_name not in self._servers:
            print(f"'{channel_name}' not in active server list. Skipping...")
            return
        print(f"Shutting down '{channel_name}'")
        server = self._servers.pop(channel_name)
        server.close()
        await server.wait_closed()
        self._locks.pop(channel_name)


    async def shutdown_all_servers(self):
        for name, server in self._servers.items():
            print(f"Shutting down server '{name}'")
            server.close()
            await server.wait_closed()
        self._servers.clear()
        self._locks.clear()

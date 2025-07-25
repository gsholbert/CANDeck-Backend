import asyncio
import websockets
import json
from routes.router import dispatch

# New version: accept only `websocket` and use websocket.path if needed
async def handle_connection(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received from Stream Deck: {data}")
            response = await dispatch(data)
            if response:
                await websocket.send(json.dumps(response))
    except Exception as e:
        print("Error handling websocket:", e)

# Updated to pass `dispatch` via closure
async def start_server(dispatch, host="localhost", port=8765):
    print(f"🔌 WebSocket server starting on ws://{host}:{port}")

    async def handler(websocket):
        websocket.dispatch = dispatch  # attach to connection
        await handle_connection(websocket)

    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever
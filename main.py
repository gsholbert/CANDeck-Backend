import asyncio
from transport.streamdeck_socket import start_server
from transport.canbus_interface import start_can_monitor, stop_can_monitor
from routes.router import dispatch
import signal

shutdown_event = asyncio.Event()

def shutdown_handler(signum, frame):
    print(f"Caught shutdown signal ({signum})")
    shutdown_event.set()

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

async def main():
    print("Starting CANDeck backend services")
    can_task = asyncio.create_task(start_can_monitor())
    server_task = asyncio.create_task(start_server(dispatch))

    await shutdown_event.wait()

    print("Cleaning up...")
    can_task.cancel()
    server_task.cancel()
    await stop_can_monitor()

if __name__ == "__main__":
    asyncio.run(main())
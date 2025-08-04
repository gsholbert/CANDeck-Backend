from pathlib import Path
from transport.canbus_interface import send_frame

async def handle_streamdeck(message, config):
    action = message.get("action")

    match action:
        case "get_snapshot_path":
            return {
                "type": "snapshot_path",
                "path": str(Path("snapshot.json").resolve())
            }
        case "send_can":
            return await handle_send_can(message)
        case _:
            # Add more Stream Deck subcommands here
            print(f"[WARN] Uknown streamdeck action: {action}")
            return {
                "type": "error",
                "message": f"Unknown streamdeck action: {action}"
            }

def register(handler_map):
    handler_map["streamdeck"] = handle_streamdeck

async def handle_send_can(msg):
    can_id = msg.get("can_id")
    data_str = msg.get("data")
    channel = msg.get("channel", "canVirtual")  # Optional override

    if not isinstance(data_str, str):
        return {
            "type": "error",
            "message": "'data' must be a comma-separated string of hex bytes"
        }

    if can_id is None or data_str is None:
        return {
            "type": "error",
            "message": "Missing 'can_id' or 'data' in message"
        }

    try:
        data = bytes([int(byte.strip(), 16) for byte in data_str.split(",")])
    except Exception as e:
        return {
            "type": "error",
            "message": f"Invalid CAN data: {e}"
        }

    try:
        await send_frame(can_id, data, channel)
        print(f"CAN send request -> ID: {can_id}, Data: {list(data)}, Channel: {channel}")
        return {
            "type": "send_can_ack",
            "can_id": can_id,
            "data": list(data),
            "channel": channel
        }
    except Exception as e:
        return {
            "type": "error",
            "message": f"Failed to send CAN frame: {e}"
        }

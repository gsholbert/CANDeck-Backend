from transport.canbus_interface import send_frame

async def handle_generic_can(message, config):
    action = message.get("action")

    match action:
        case "send":
            return await handle_send_can(message)
        case _:
            print(f"[WARN] Unknown generic CAN action: {action}")
            return {
                "type": "error",
                "message": f"Unknown CAN action: {action}"
            }

def register(handler_map):
    handler_map["can"] = handle_generic_can

async def handle_send_can(msg):
    can_id = msg.get("can_id")
    data_str = msg.get("data")
    channel = msg.get("channel", "canVirtual")

    if can_id is None or data_str is None:
        return {
            "type": "error",
            "message": "Missing 'can_id' or 'data' in message"
        }

    if not isinstance(data_str, str):
        return {
            "type": "error",
            "message": "'data' must be a comma-separated string of hex bytes"
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
        print(f"[CAN] Sent frame: ID={can_id}, Data={list(data)}, Channel={channel}")
        return {
            "type": "ack",
            "message": "CAN frame sent",
            "can_id": can_id,
            "data": list(data),
            "channel": channel
        }
    except Exception as e:
        return {
            "type": "error",
            "message": f"Failed to send CAN frame: {e}"
        }

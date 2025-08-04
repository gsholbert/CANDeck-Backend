from routes.handlers import handler_map

async def dispatch(message):
    msg_type = message.get("type")
    if not msg_type:
        return {"type": "error", "message": "Missing 'type' in message"}
    handler = handler_map.get(msg_type)

    if handler:
        response = await handler(message)
        return response if response is not None else {"type": "ack", "message": "No response"}
    else:
        print(f"[WARN] Unknown Command: {msg_type}")
        return {"type": "error", "message": f"Unknown command: {msg_type}"}
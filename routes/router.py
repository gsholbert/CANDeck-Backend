from routes import handler_map

async def dispatch(message):
    msg_type = message.get("type")
    handler = handler_map.get(msg_type)

    if handler:
        return await handler(message)
    else:
        print(f"[WARN] Unknown Command: {msg_type}")
        return {"type": "error", "message": f"Unknown command: {msg_type}"}
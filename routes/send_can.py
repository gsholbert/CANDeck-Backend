async def handle_send_can(msg):
    can_id = msg.get("can_id")
    data_str = msg.get("data")

    try:
        data = [int(byte.strip(), 16) for byte in data_str.split(",")]
        print(f"CAN send request -> ID: {can_id}, Data: {data}")
        # TODO: send to CAN here
    except Exception as e:
        print("Error parsing CAN data:", e)
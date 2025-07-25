import yaml
import can
from transport import config, signal_schema, active_signals, last_values

def create_can_bus(channel_name="canVirtual"):
    buscfg = config.get("can_interfaces", {}).get(channel_name, {})

    interface = buscfg.get("interface", "socketcan")
    channel = buscfg.get("channel", "can0")
    bitrate = buscfg.get("bitrate", "500000")
    receive_own_messages = buscfg.get("receive_own_messages", False)

    return can.Bus(
        interface=interface,
        channel=channel,
        bitrate=bitrate,
        receive_own_messages=receive_own_messages
    )
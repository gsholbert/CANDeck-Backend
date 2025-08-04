import can
import asyncio
from utils.utils import should_update, write_snapshot
from typing import Dict, Any
from core.constants import Config, State
from core.app_contexts import Managers

def parse_signal(msg, signal) -> Dict[str, Any]:
    spec = Config.schema.get(signal)
    if not spec or msg.arbitration_id != int(spec["can_id"], 16):
        return {}
    
    start = spec["byte"]
    end = start + spec["length"]
    raw_bytes = msg.data[start:end]

    if len(raw_bytes) < spec["length"]:
        return {}
    
    signed = spec.get("signed", False)
    value = int.from_bytes(raw_bytes, byteorder="big", signed=signed)
    
    if "status_flags" in spec:
        return {
            f"{signal}.{name}": bool(value &  (1 << bit))
            for name, bit in spec["status_flags"].items()
        }
    
    if "mask" in spec:
        value &= int(spec["mask"], 16)
    if "shift" in spec:
        value >>= spec["shift"]

    value *= spec.get("scale", 1.0)
    value += spec.get("offset", 0)
    
    return {signal: value}

async def start_can_monitor():
    print(f"[DEBUG] Loaded ECU Channel: {Config.data.get('ecu', {}).get('channel')}")
    ecu_config = Config.data.get("ecu", {})
    channel = ecu_config.get("channel", "canVirtual")

    bus = await Managers.bus_manager.get_bus(channel)
    Managers.bus_manager._bus_lifecycles[channel] = "permanent" # Override bus as permanent
    reader = can.AsyncBufferedReader()
    notifier = can.Notifier(bus, [reader], loop=asyncio.get_running_loop())

    State.active_signals.update(Config.schema.keys())

    try:
        while True:
            msg = await reader.get_message()
            snapshot: Dict[str, Any] = {}
            for signal in State.active_signals:
                parsed = parse_signal(msg, signal)
                for name, val in parsed.items():
                    if should_update(name, val):
                        snapshot[name] = val
            if snapshot:
                write_snapshot(snapshot)

    except asyncio.CancelledError:
        print("CAN monitor cancelled")
    finally:
        notifier.stop()

async def send_frame(can_id: int, data: bytes, channel: str = "canVirtual"):
    bus = await Managers.bus_manager.get_bus(channel)
    try:
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
        bus.send(msg)
    except Exception as e:
        print(f"Error sending CAN Frame: {e}")
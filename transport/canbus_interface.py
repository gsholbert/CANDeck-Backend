import can
import asyncio
from utils.utils import should_update, write_snapshot
from typing import Dict, Any
from can import Message
from transport import signal_schema, active_signals, config
from bus_manager import create_can_bus

bus = None
reader = None
notifier = None

shutdown_event = asyncio.Event()

def parse_signal(msg, signal) -> Dict[str, Any]:
    spec = signal_schema.get(signal)
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
    global bus, reader, notifier
    bus = create_can_bus()
    reader = can.AsyncBufferedReader()
    notifier = can.Notifier(bus, [reader], loop=asyncio.get_running_loop())

    active_signals.update(signal_schema.keys())

    try:
        while True:
            msg = await reader.get_message()
            snapshot: Dict[str, Any]= {}
            for signal in active_signals:
                parsed = parse_signal(msg, signal)
                for name, val in parsed.items():
                    if should_update(name, val):
                        snapshot[name] = val
            if snapshot:
                write_snapshot(snapshot)

    except asyncio.CancelledError:
        print("CAN monitor cancelled")
    finally:
        await stop_can_monitor()

async def stop_can_monitor():
    global notifier, bus
    if notifier:
        notifier.stop()
        print("Notifier Stopped")
    if bus:
        bus.shutdown()
        print("CAN bus shutdown")

def send_frame(can_id, data, bus):
    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
    bus.send(msg)
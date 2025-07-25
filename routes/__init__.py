from .send_can import handle_send_can
from .get_snapshot_path import handle_get_snapshot_path

handler_map = {
    "send_can": handle_send_can,
    "get_snapshot_path": handle_get_snapshot_path
}
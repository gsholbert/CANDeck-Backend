from pathlib import Path

async def handle_get_snapshot_path(message):
    return{
        "type": "snapshot_path",
        "path": str(Path("snapshot.json").resolve())
    }
import cantools
import json
from pathlib import Path
import argparse
import sys

def dbc_to_json(dbc_path: Path, json_output_path: Path):
    if not dbc_path.exists() or not dbc_path.is_file():
        print(f"Error: DBC file '{dbc_path}' not found or not a file.")
        sys.exit(1)

    try:
        db = cantools.database.load_file(dbc_path, strict=False)
    except Exception as e:
        print(f"Error loading DBC file: {e}")
        sys.exit(1)

    result = {}
    for message in db.messages:
        for signal in message.signals:
            signal_entry = {
                "can_id": hex(message.frame_id),
                "byte": signal.start // 8,
                "length": (signal.length + 7) // 8,
                "scale": signal.scale,
                "offset": signal.offset,
                "signed": signal.is_signed
            }

            if signal.choices:
                signal_entry["status_flags"] = {
                    int(choice.value): str(choice.name) for choice in signal.choices.values()
                }

            result[signal.name] = signal_entry

    try:
        with open(json_output_path, "w") as f:
            json.dump(result, f, indent=4)
        print(f"Successfully wrote JSON to: {json_output_path}")
    except Exception as e:
        print(f"Failed to write JSON: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert DBC to simplified JSON schema.")
    parser.add_argument("dbc_path", type=Path, help="Path to the DBC file.")
    parser.add_argument("json_output_path", type=Path, help="Path to write the JSON output.")

    args = parser.parse_args()
    dbc_to_json(args.dbc_path, args.json_output_path)


if __name__ == "__main__":
    main()
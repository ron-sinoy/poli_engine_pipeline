import json
from pathlib import Path
from typing import Any

def write_json_file(path: str | Path, payload: Any) -> None:
    """Write a plain JSON file for gold-stage results."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")

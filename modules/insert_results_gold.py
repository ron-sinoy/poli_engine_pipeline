import json
from pathlib import Path
from typing import Any

from modules.progress_log import log_step


def write_json_file(path: str | Path, payload: Any) -> None:
    """Write a plain JSON file for gold-stage results."""
    output_path = Path(path)
    log_step(f"Preparing plain JSON write for {output_path}.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")
    log_step(f"Plain JSON write complete for {output_path}.")

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_bronze_sources() -> list[dict[str, Any]]:
    # Parse bronze_sources.json and return as a list of {source, apis} dicts
    config_path = PROJECT_ROOT / "bronze_sources.json"
    parsed_sources = json.loads(config_path.read_text(encoding="utf-8"))
    expanded_sources = []
    for name, apis in parsed_sources.items():
        expanded_sources.append({
            "source": name,
            "apis": apis
        })
    return expanded_sources
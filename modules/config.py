import json
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOTENV_PATH = PROJECT_ROOT / ".env.example"


def get_bronze_sources() -> list[dict[str, Any]]:
    load_dotenv(DOTENV_PATH, override=False)

    config_path = Path(os.getenv("BRONZE_SOURCES_FILE", PROJECT_ROOT / "bronze_sources.json"))
    parsed_sources = json.loads(config_path.read_text(encoding="utf-8"))

    return [{"source": name, "apis": apis} for name, apis in parsed_sources.items()]
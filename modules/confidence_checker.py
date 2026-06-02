import json
from pathlib import Path
from typing import Any


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def confidence_checker(political_items: list[dict[str, Any]]) -> bool:
    params = _load_params()
    benchmark_confidence = float(params["confidence_level"])

    for political_item in political_items:
        if political_item.get("thread_id") is None:
            return False
        if float(political_item["confidence_level"]) < benchmark_confidence:
            return False

    return True

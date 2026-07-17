import json
from pathlib import Path
from typing import Any


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def waiting_list_confidence_checker(waiting_list_items: list[dict[str, Any]]) -> bool:
    params = _load_params()
    benchmark_confidence = float(params["confidence_level"])
    required_matches = int(params["required_waiting_list_matches"])

    for waiting_list_item in waiting_list_items:
        incident_list = waiting_list_item.get("incidentList", [])
        top_incidents = incident_list[:required_matches]
        if len(top_incidents) < required_matches:
            return False

        for incident in top_incidents:
            if float(incident["confidence_score"]) < benchmark_confidence:
                return False

    return True

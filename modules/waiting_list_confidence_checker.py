import json
from pathlib import Path
from typing import Any


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def waiting_list_confidence_checker(waiting_list_items: list[dict[str, Any]]) -> bool:
    params = _load_params()
    benchmark_confidence = float(params["confidence_level"])

    for waiting_list_item in waiting_list_items:
        incident_list = waiting_list_item.get("incidentList", [])
        top_two_incidents = incident_list[:2]
        if len(top_two_incidents) < 2:
            return False

        for incident in top_two_incidents:
            if float(incident["confidence_score"]) < benchmark_confidence:
                return False

    return True

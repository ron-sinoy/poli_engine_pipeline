import json
from pathlib import Path
from typing import Any

from modules.compare_vectors import top_n_threads_classifier
from modules.fetch_api import fetch_api


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"
WAITING_LIST_VECTORS_URL = "https://poli-engine-backend.onrender.com/vector_waiting_list_incidents"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def _normalize_waiting_list_vectors(waiting_list_vectors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_vectors: list[dict[str, Any]] = []
    for waiting_list_item in waiting_list_vectors:
        normalized_vectors.append(
            {
                "thread_id": waiting_list_item["id"],
                "title": str(waiting_list_item["id"]),
                "summary": "",
                "thread_vectors": waiting_list_item.get("vectors", []),
            }
        )

    return normalized_vectors


def vector_waiting_list_incidents(
    vector_ref: Any,
    *,
    count: int | None = None,
) -> list[dict[str, Any]]:
    params = _load_params()
    resolved_count = count if count is not None else int(params["count_level_waiting_list_incidents"])
    waiting_list_vectors = fetch_api(WAITING_LIST_VECTORS_URL)
    if isinstance(waiting_list_vectors, dict):
        waiting_list_vectors = waiting_list_vectors.get("waiting_list_incidents", waiting_list_vectors.get("data", []))

    normalized_vectors = _normalize_waiting_list_vectors(waiting_list_vectors)
    ranked_incidents = top_n_threads_classifier(
        vector_ref,
        normalized_vectors,
        resolved_count,
        confidence_level=0.0,
    )

    waiting_list_lookup = {item["id"]: item for item in waiting_list_vectors}
    incident_list: list[dict[str, Any]] = []
    for ranked_item in ranked_incidents:
        matched_waiting_list_item = waiting_list_lookup.get(ranked_item["thread_id"], {})
        incident_item = {
            "id": matched_waiting_list_item.get("id", ranked_item["thread_id"]),
            "vectors": matched_waiting_list_item.get("vectors", []),
            "scores": ranked_item["scores"],
        }
        if matched_waiting_list_item.get("source_url") is not None:
            incident_item["source_url"] = matched_waiting_list_item["source_url"]
        incident_list.append(incident_item)

    return incident_list

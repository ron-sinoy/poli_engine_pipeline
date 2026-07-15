import json
from pathlib import Path
from typing import Any

from modules.fetch_api import post_api


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"
WAITING_LIST_MATCH_URL = "https://poli-engine-backend.onrender.com/waitinglists/match"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def vector_waiting_list_incidents(
    vector_ref: Any,
    *,
    count: int | None = None,
) -> list[dict[str, Any]]:
    """Return the waiting-list incidents most similar to vector_ref.

    Postgres does the ranking and returns content, source_url and a real cosine
    score. Previously every row's 3072-dim vector was downloaded and cosined in
    Python -- ~48MB, which exceeded the Supabase statement timeout, so this
    always came back empty and every article fell through to the waiting list.
    """
    params = _load_params()
    resolved_count = count if count is not None else int(params["count_level_waiting_list_incidents"])

    matched_incidents = post_api(
        WAITING_LIST_MATCH_URL,
        {
            "vectors": vector_ref,
            "match_count": resolved_count,
        },
    )

    return [
        {
            "id": matched_incident["id"],
            "content": matched_incident.get("content"),
            "source_url": matched_incident.get("source_url"),
            "source_id": matched_incident.get("source_id"),
            "confidence_score": matched_incident.get("score"),
        }
        for matched_incident in matched_incidents
    ]

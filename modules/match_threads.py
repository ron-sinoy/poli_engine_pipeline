import json
from pathlib import Path
from typing import Any

from modules.fetch_api import post_api


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"
THREADS_MATCH_URL = "https://poli-engine-backend.onrender.com/threads/match"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


def match_threads(
    vector_ref: Any,
    *,
    count: int | None = None,
) -> list[dict[str, Any]]:
    """Return the threads most similar to vector_ref, ranked by real cosine score.

    Threads with no vector are skipped by the RPC, so only threads that can
    actually be compared are returned.
    """
    params = _load_params()
    resolved_count = count if count is not None else int(params["count_level_primary_threads"])

    matched_threads = post_api(
        THREADS_MATCH_URL,
        {
            "vectors": vector_ref,
            "match_count": resolved_count,
        },
    )

    return [
        {
            "thread_id": matched_thread["thread_id"],
            "title": matched_thread.get("title"),
            "summary": matched_thread.get("summary"),
            "scores": matched_thread.get("score"),
        }
        for matched_thread in matched_threads
    ]

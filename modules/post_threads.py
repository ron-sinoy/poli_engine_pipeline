from typing import Any

import httpx


THREADS_URL = "https://poli-engine-backend.onrender.com/threads"


def post_threads(title: str, summary: str, vectors: Any = None) -> Any:
    payload = {
        "title": title,
        "summary": summary,
    }
    if vectors is not None:
        payload["vectors"] = vectors

    response = httpx.post(
        THREADS_URL,
        json=payload,
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("thread_id", payload)

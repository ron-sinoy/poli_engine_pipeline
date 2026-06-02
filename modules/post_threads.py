from typing import Any

import httpx


THREADS_URL = "https://poli-engine-backend-production.up.railway.app/threads"


def post_threads(title: str, summary: str) -> Any:
    response = httpx.post(
        THREADS_URL,
        json={
            "title": title,
            "summary": summary,
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("thread_id", payload)

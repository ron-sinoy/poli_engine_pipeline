from typing import Any

import httpx


WAITING_LISTS_URL = "https://poli-engine-backend.onrender.com/waitinglists"


def post_waitinglists(content: str, vector: Any, source_url: str) -> Any:
    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError("source_url must be a non-empty string")
    response = httpx.post(
        WAITING_LISTS_URL,
        json={
            "content": content,
            "vectors": vector,
            "source_url": source_url.strip(),
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

from typing import Any

import httpx


WAITING_LISTS_URL = "https://poli-engine-backend-production.up.railway.app/waitinglists"


def post_waitinglists(content: str, vector: Any) -> Any:
    response = httpx.post(
        WAITING_LISTS_URL,
        json={
            "content": content,
            "vectors": vector,
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

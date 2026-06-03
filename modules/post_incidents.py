from typing import Any

import httpx


INCIDENTS_URL = "https://poli-engine-backend-production.up.railway.app/incidents"


def post_incidents(thread_id: Any, para_content: str) -> Any:
    response = httpx.post(
        INCIDENTS_URL,
        json={
            "thread_id": thread_id,
            "para_content": para_content,
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

from typing import Any

import httpx


SOURCE_IDS_URL = "https://poli-engine-backend-production.up.railway.app/sourceids/update"


def update_db(source_id: str, status: str) -> Any:
    response = httpx.post(
        SOURCE_IDS_URL,
        json={
            "source_id": source_id,
            "status": status,
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

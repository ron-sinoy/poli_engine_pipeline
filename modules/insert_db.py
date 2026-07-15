from typing import Any

import httpx


SOURCE_IDS_URL = "https://poli-engine-backend.onrender.com/sourceids"


def insert_db(source_id: str) -> Any:
    response = httpx.post(
        SOURCE_IDS_URL,
        json={
            "source_id": source_id,
            "status": "processing",
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

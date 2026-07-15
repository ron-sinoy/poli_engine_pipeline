from typing import Any

import httpx


SOURCE_IDS_URL = "https://poli-engine-backend.onrender.com/sourceids"


def get_source_ids() -> list[dict[str, Any]]:
    response = httpx.get(SOURCE_IDS_URL, follow_redirects=True, timeout=30)
    response.raise_for_status()
    return response.json()


def check_db(source_ids: list[dict[str, Any]], source_id: str) -> bool:
    for source_id_item in source_ids:
        if (
            source_id_item["source_id"] == source_id
            and source_id_item["status"] in ["completed", "filtered"]
        ):
            return True

    return False

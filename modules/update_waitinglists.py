from typing import Any

import httpx


WAITING_LISTS_UPDATE_URL = "https://poli-engine-backend.onrender.com/waitinglists/update"


def update_waitinglists(waiting_list_id: Any, status: str) -> Any:
    response = httpx.post(
        WAITING_LISTS_UPDATE_URL,
        json={
            "id": waiting_list_id,
            "status": status,
        },
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

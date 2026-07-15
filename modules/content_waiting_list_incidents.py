from typing import Any

from modules.fetch_api import fetch_api


CONTENT_WAITING_LIST_INCIDENTS_URL = "https://poli-engine-backend.onrender.com/content_waiting-list_incidents"


def _normalize_content_waiting_list_incidents(
    content_waiting_list_incidents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_content_waiting_list_incidents: list[dict[str, Any]] = []
    for waiting_list_item in content_waiting_list_incidents:
        normalized_content_waiting_list_incidents.append(
            {
                "id": waiting_list_item["id"],
                "content": waiting_list_item.get("content"),
            }
        )

    return normalized_content_waiting_list_incidents


def content_waiting_list_incidents() -> list[dict[str, Any]]:
    waiting_list_incidents = fetch_api(CONTENT_WAITING_LIST_INCIDENTS_URL)
    if isinstance(waiting_list_incidents, dict):
        waiting_list_incidents = waiting_list_incidents.get(
            "waiting_list_incidents",
            waiting_list_incidents.get("data", []),
        )

    return _normalize_content_waiting_list_incidents(waiting_list_incidents)

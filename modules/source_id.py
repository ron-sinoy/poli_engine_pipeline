from typing import Any


def relabel_source_id(source: str, payload: dict[str, Any]) -> dict[str, Any]:
    if source == "mathrubhumi":
        payload["source_id"] = f"mt_#{payload['contentID']}"
        del payload["contentID"]
    else:
        payload = payload

    return payload

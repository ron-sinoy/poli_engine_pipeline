from typing import Any


def filter_json_values(payload: dict[str, Any], key: str, values: list[Any]) -> bool:
    return payload[key] in values


def filter_json_keys(payload: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    filtered_payload: dict[str, Any] = {}

    for key in keys:
        if key in payload:
            filtered_payload[key] = payload[key]

    return filtered_payload

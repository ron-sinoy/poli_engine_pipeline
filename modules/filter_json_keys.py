from typing import Any

def filter_json_keys(payload: Any, keys: list[Any]) -> Any:
    """Return a new JSON structure containing only matching keys and subtrees."""
    key_set = set(keys)
    return _filter_json_keys(payload, key_set)


def _filter_json_keys(payload: Any, key_set: set[Any]) -> Any:
    if isinstance(payload, dict):
        filtered: dict[Any, Any] = {}
        for key, value in payload.items():
            if key in key_set:
                filtered[key] = value
                continue

            nested = _filter_json_keys(value, key_set)
            if nested is not None:
                filtered[key] = nested

        return filtered or None

    if isinstance(payload, list):
        filtered_items = []
        for item in payload:
            nested = _filter_json_keys(item, key_set)
            if nested is not None:
                filtered_items.append(nested)

        return filtered_items or None

    return None

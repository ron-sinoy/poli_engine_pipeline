from typing import Any

def filter_json_values(payload: Any, key: Any, values: list[Any]) -> Any:
    """Return the original payload when any matching key has an allowed value."""
    matched = _has_matching_value(payload, key, values)
    return payload if matched else None


def _has_matching_value(payload: Any, key: Any, values: list[Any]) -> bool:
    if isinstance(payload, dict):
        for current_key, current_value in payload.items():
            if current_key == key and current_value in values:
                return True

            if _has_matching_value(current_value, key, values):
                return True

        return False

    if isinstance(payload, list):
        return any(_has_matching_value(item, key, values) for item in payload)

    return False

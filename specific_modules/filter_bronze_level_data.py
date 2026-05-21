from typing import Any

from modules.filter_json_values import filter_json_values


ALLOWED_ELEMENT_TYPES = [0, 1]
ALLOWED_SECTION_TITLES = ["News"]
ALLOWED_SUBSECTION_TITLES = ["Kerala", "India"]
SECTION_KEYS = ("sectionTitle", "sectionTiles")
SUBSECTION_KEYS = ("subSectionTitle", "subsectionTitle")


def filter_bronze_level_data(bronze_level_data: Any) -> Any:
    """Keep only bronze-level content objects that match the Tasklist filters."""
    return _filter_components(bronze_level_data)


def _filter_components(payload: Any) -> Any:
    if isinstance(payload, list):
        filtered_items = []
        for item in payload:
            filtered_item = _filter_components(item)
            if filtered_item is not None:
                filtered_items.append(filtered_item)

        return filtered_items

    if isinstance(payload, dict):
        filtered: dict[Any, Any] = {}
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                nested = _filter_components(value)
                if nested is not None:
                    filtered[key] = nested
                continue

            filtered[key] = value

        if _is_content_component(payload):
            matched = _matches_tasklist_filters(payload)
            return filtered if matched else None

        return filtered or None

    return payload


def _is_content_component(payload: dict[Any, Any]) -> bool:
    return any(
        key in payload
        for key in ("elementType", *SECTION_KEYS, *SUBSECTION_KEYS, "itemTitle")
    )


def _matches_tasklist_filters(payload: dict[Any, Any]) -> bool:
    return (
        _matches_values(payload, "elementType", ALLOWED_ELEMENT_TYPES)
        and _matches_any_key(payload, SECTION_KEYS, ALLOWED_SECTION_TITLES)
        and _matches_any_key(payload, SUBSECTION_KEYS, ALLOWED_SUBSECTION_TITLES)
    )


def _matches_any_key(
    payload: dict[Any, Any], keys: tuple[str, ...], allowed_values: list[Any]
) -> bool:
    for key in keys:
        if _matches_values(payload, key, allowed_values):
            return True

    return False


def _matches_values(payload: dict[Any, Any], key: str, allowed_values: list[Any]) -> bool:
    if key not in payload:
        return False

    return filter_json_values({key: payload[key]}, key, allowed_values) is not None

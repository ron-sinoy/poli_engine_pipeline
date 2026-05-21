from typing import Any

from modules.fetch_api import fetch_api
from modules.filter_json_keys import filter_json_keys
from modules.filter_json_values import filter_json_values


SILVER_ITEM_KEYS = [
    "elementType",
    "sectionTitle",
    "subSectionTitle",
    "itemTitle",
    "itemTitleLead",
    "itemDetailURL",
    "contentID",
    "publishedTime",
]
DETAILS_BASE_URL = "https://www.mathrubhumi.com"


def enrich_silver_level_data(silver_base_data: Any) -> Any:
    """Reduce silver items to Tasklist keys and attach merged detail content."""
    if not isinstance(silver_base_data, list):
        return []

    enriched_items = []
    for item in silver_base_data:
        enriched_item = _enrich_silver_item(item)
        if enriched_item is not None:
            enriched_items.append(enriched_item)
    return enriched_items


def _enrich_silver_item(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    filtered_item = filter_json_keys(item, SILVER_ITEM_KEYS)
    if not isinstance(filtered_item, dict):
        return None

    enriched_item = dict(filtered_item)
    detail_url = enriched_item.get("itemDetailURL")
    enriched_item["content"] = _extract_content(detail_url)
    return enriched_item


def _extract_content(detail_url: Any) -> str:
    detail_payload = _fetch_detail_payload(detail_url)
    if not isinstance(detail_payload, dict):
        return ""

    detail_elements = detail_payload.get("detail_elements")
    if not isinstance(detail_elements, list):
        return ""

    filtered_elements = []
    for element in detail_elements:
        filtered_element = filter_json_values(element, "elementType", [0])
        if isinstance(filtered_element, dict):
            filtered_elements.append(filtered_element)

    return merge_content(filtered_elements)


def _fetch_detail_payload(detail_url: Any) -> Any:
    if not isinstance(detail_url, str) or not detail_url:
        return None

    full_url = _build_full_url(detail_url)
    try:
        return fetch_api(full_url)
    except Exception:
        return None


def merge_content(elements: list[dict[str, Any]]) -> str:
    merged_parts = []
    for element in elements:
        element_content = element.get("elementContent")
        if isinstance(element_content, str) and element_content:
            merged_parts.append(element_content)

    return "\n\n".join(merged_parts)


def _build_full_url(detail_url: str) -> str:
    if detail_url.startswith(("http://", "https://")):
        return detail_url

    if detail_url.startswith("/"):
        return f"{DETAILS_BASE_URL}{detail_url}"

    return f"{DETAILS_BASE_URL}/{detail_url}"

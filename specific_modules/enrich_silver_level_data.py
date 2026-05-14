from typing import Any

from modules.fetch_api import fetch_api
from modules.filter_json_keys import filter_json_keys
from modules.filter_json_values import filter_json_values
from modules.progress_log import describe_payload, log_step


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
        log_step("Silver base data was not a list; returning empty list.")
        return []

    log_step(f"Starting silver enrichment for {len(silver_base_data)} item(s).")
    enriched_items = []
    for index, item in enumerate(silver_base_data, start=1):
        log_step(f"Enriching silver item {index} of {len(silver_base_data)}.")
        enriched_item = _enrich_silver_item(item)
        if enriched_item is not None:
            enriched_items.append(enriched_item)
            log_step(f"Silver item {index} enrichment succeeded.")
        else:
            log_step(f"Silver item {index} enrichment returned None.")

    log_step(f"Silver enrichment complete with {len(enriched_items)} item(s).")
    return enriched_items


def _enrich_silver_item(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        log_step("Skipped silver item because it was not a dict.")
        return None

    filtered_item = filter_json_keys(item, SILVER_ITEM_KEYS)
    if not isinstance(filtered_item, dict):
        log_step("Skipped silver item because key filtering did not return a dict.")
        return None

    enriched_item = dict(filtered_item)
    detail_url = enriched_item.get("itemDetailURL")
    log_step(f"Extracting detail content for itemDetailURL={detail_url!r}.")
    enriched_item["content"] = _extract_content(detail_url)
    log_step(
        "Finished detail extraction for silver item with content summary "
        f"{describe_payload(enriched_item['content'])}."
    )
    return enriched_item


def _extract_content(detail_url: Any) -> str:
    detail_payload = _fetch_detail_payload(detail_url)
    if not isinstance(detail_payload, dict):
        log_step("Detail payload was not a dict; returning empty content.")
        return ""

    detail_elements = detail_payload.get("detail_elements")
    if not isinstance(detail_elements, list):
        log_step("Detail payload had no detail_elements list; returning empty content.")
        return ""

    log_step(f"Filtering {len(detail_elements)} detail element(s) for text content.")
    filtered_elements = []
    for element in detail_elements:
        filtered_element = filter_json_values(element, "elementType", [0])
        if isinstance(filtered_element, dict):
            filtered_elements.append(filtered_element)
            log_step("Accepted a detail element with elementType=0.")

    log_step(f"Merging {len(filtered_elements)} filtered detail element(s).")
    return merge_content(filtered_elements)


def _fetch_detail_payload(detail_url: Any) -> Any:
    if not isinstance(detail_url, str) or not detail_url:
        log_step("Skipped detail fetch because detail_url was empty or invalid.")
        return None

    full_url = _build_full_url(detail_url)
    log_step(f"Fetching silver detail payload from {full_url}.")
    try:
        payload = fetch_api(full_url)
        log_step(f"Finished detail fetch from {full_url} with {describe_payload(payload)}.")
        return payload
    except Exception as error:
        log_step(f"Detail fetch failed for {full_url}: {error!r}.")
        return None


def merge_content(elements: list[dict[str, Any]]) -> str:
    merged_parts = []
    for element in elements:
        element_content = element.get("elementContent")
        if isinstance(element_content, str) and element_content:
            merged_parts.append(element_content)
            log_step("Added elementContent chunk to merged silver content.")

    merged_content = "\n\n".join(merged_parts)
    log_step(f"Merged silver content length is {len(merged_content)}.")
    return merged_content


def _build_full_url(detail_url: str) -> str:
    if detail_url.startswith(("http://", "https://")):
        log_step(f"Detail URL already absolute: {detail_url}.")
        return detail_url

    if detail_url.startswith("/"):
        full_url = f"{DETAILS_BASE_URL}{detail_url}"
        log_step(f"Built absolute detail URL: {full_url}.")
        return full_url

    full_url = f"{DETAILS_BASE_URL}/{detail_url}"
    log_step(f"Built absolute detail URL: {full_url}.")
    return full_url

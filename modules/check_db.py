from typing import Any

import httpx

from modules.fetch_thread_list import BACKEND_BASE_URL
from modules.fetch_api import fetch_api
from modules.progress_log import describe_payload, log_step


def get_sourceids(base_url: str = BACKEND_BASE_URL) -> set[str]:
    """Fetch source ids from the backend and normalize them into a lookup set."""
    url = f"{base_url.rstrip('/')}/sourceids"
    log_step(f"Fetching source ids from {url}.")
    payload = fetch_api(url)
    sourceids = _collect_sourceids(payload)
    log_step(f"Loaded {len(sourceids)} source id(s) from {url}.")
    return sourceids


def filter_items_with_new_sourceids(items: Any, existing_sourceids: set[str]) -> list[dict[str, Any]]:
    """Return only items whose contentID is present and not already stored."""
    if not isinstance(items, list):
        log_step("Source id filtering input was not a list; returning empty list.")
        return []

    accepted_items: list[dict[str, Any]] = []
    seen_sourceids = set(existing_sourceids)
    skipped_missing = 0
    skipped_existing = 0

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            log_step(f"Skipped source id filtering item {index} because it was not a dict.")
            continue

        content_id = _normalize_sourceid(item.get("contentID"))
        if content_id is None:
            skipped_missing += 1
            log_step(
                f"Skipped source id filtering item {index} because contentID was missing."
            )
            continue

        if content_id in seen_sourceids:
            skipped_existing += 1
            log_step(
                f"Skipped source id filtering item {index} because contentID={content_id!r} already exists."
            )
            continue

        seen_sourceids.add(content_id)
        accepted_items.append(item)
        log_step(
            f"Accepted source id filtering item {index} with contentID={content_id!r}."
        )

    log_step(
        "Source id filtering kept "
        f"{len(accepted_items)} item(s), skipped {skipped_existing} existing and "
        f"{skipped_missing} missing contentID item(s)."
    )
    return accepted_items


def post_sourceids(items: Any, base_url: str = BACKEND_BASE_URL) -> list[Any]:
    """POST the processed items' content IDs to the backend sourceids store."""
    if not isinstance(items, list):
        log_step("Source id posting input was not a list; returning empty response list.")
        return []

    url = f"{base_url.rstrip('/')}/sourceids"
    responses: list[Any] = []

    log_step(f"Preparing to post {len(items)} source id item(s) to {url}.")
    for index, item in enumerate(items, start=1):
        payload = _build_sourceid_post_payload(item, index)
        if payload is None:
            continue

        log_step(
            f"Posting source id {index}/{len(items)} with source_id={payload['source_id']!r}."
        )
        response = httpx.post(url, json=payload, timeout=None)
        log_step(
            "Received source id POST response "
            f"{response.status_code} for item {index}/{len(items)}."
        )
        response.raise_for_status()
        parsed_response = _parse_response_body(response)
        responses.append(parsed_response)
        log_step(
            "Stored source id POST response payload "
            f"{describe_payload(parsed_response)} for item {index}/{len(items)}."
        )

    log_step(f"Completed posting {len(responses)} source id item(s) to {url}.")
    return responses


def _build_sourceid_post_payload(
    item: Any, index: int
) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        log_step(f"Skipped source id POST item {index} because it was not a dict.")
        return None

    content_id = _normalize_sourceid(item.get("contentID"))
    if content_id is None:
        log_step(f"Skipped source id POST item {index} because contentID was missing.")
        return None

    payload = {"source_id": content_id}
    log_step(f"Built source id POST payload {describe_payload(payload)}.")
    return payload


def _collect_sourceids(payload: Any) -> set[str]:
    collected_sourceids: set[str] = set()
    _walk_sourceids(payload, collected_sourceids)
    return collected_sourceids


def _walk_sourceids(payload: Any, collected_sourceids: set[str]) -> None:
    if isinstance(payload, str):
        normalized = _normalize_sourceid(payload)
        if normalized is not None:
            collected_sourceids.add(normalized)
        return

    if isinstance(payload, dict):
        if any(key in payload for key in {"source_id", "sourceId", "contentId", "contentID"}):
            for key in ("source_id", "sourceId", "contentId", "contentID"):
                normalized = _normalize_sourceid(payload.get(key))
                if normalized is not None:
                    collected_sourceids.add(normalized)
            return

        for key, value in payload.items():
            if key in {
                "sourceids",
                "sourceIds",
                "source_ids",
                "source_id",
                "contentIds",
                "content_ids",
                "items",
                "rows",
                "results",
                "data",
            }:
                _walk_sourceids(value, collected_sourceids)
        return

    if isinstance(payload, list):
        for item in payload:
            _walk_sourceids(item, collected_sourceids)


def _normalize_sourceid(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None

    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)

    return None


def _parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text = response.text.strip()
        return text or None

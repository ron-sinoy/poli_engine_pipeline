from typing import Any

import httpx

from modules.fetch_thread_list import BACKEND_BASE_URL


def create_thread(title: str, summary: str, base_url: str = BACKEND_BASE_URL) -> dict[str, Any]:
    """Create a new backend thread and return the parsed response payload."""
    normalized_title = _require_text(title, "title")
    normalized_summary = _require_text(summary, "summary")
    payload = {
        "title": normalized_title,
        "summary": normalized_summary,
    }
    url = f"{base_url.rstrip('/')}/threads"

    response = httpx.post(url, json=payload, timeout=None)
    response.raise_for_status()
    parsed_response = _parse_response_body(response)
    return parsed_response


def extract_thread_id(create_thread_response: Any) -> int:
    """Extract the created thread_id from a backend create-thread response."""
    if not isinstance(create_thread_response, dict):
        raise ValueError("Thread creation response must be a dict.")

    thread_id = create_thread_response.get("thread_id")
    if isinstance(thread_id, bool):
        raise ValueError("Thread creation response thread_id cannot be boolean.")
    if isinstance(thread_id, int):
        return thread_id
    if isinstance(thread_id, str) and thread_id.strip().isdigit():
        return int(thread_id.strip())

    raise ValueError("Thread creation response did not include a valid thread_id.")


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Thread creation field {field_name} must be a non-empty string.")
    return value.strip()


def _parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text = response.text.strip()
        return text or None

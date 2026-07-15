from typing import Any
import httpx

INCIDENTS_URL = "https://poli-engine-backend.onrender.com/incidents"

def _normalize_thread_id(thread_id: Any) -> int:
    if isinstance(thread_id, bool):
        raise ValueError("thread_id must be an integer, not a boolean")
    if isinstance(thread_id, int):
        return thread_id
    if isinstance(thread_id, str) and thread_id.strip().isdigit():
        return int(thread_id.strip())
    raise ValueError("thread_id must be an integer or a numeric string")


def post_incidents(
    thread_id: Any,
    body: str,
    source_url: str,
    persons_involved: list[int] | None = None,
) -> Any:
    normalized_thread_id = _normalize_thread_id(thread_id)
    if not isinstance(body, str) or not body.strip():
        raise ValueError("body must be a non-empty string")
    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError("source_url must be a non-empty string")
    if persons_involved is None:
        persons_involved = []
    if not isinstance(persons_involved, list):
        raise ValueError("persons_involved must be a list")

    response = httpx.post(
        INCIDENTS_URL,
        json={
            "thread_id": normalized_thread_id,
            "body": body.strip(),
            "source_url": source_url.strip(),
            "persons_involved": persons_involved,
        },
        follow_redirects=True,
        timeout=30,
    )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"Incident post failed with HTTP {response.status_code}: {response.text}"
        ) from error
    return response.json()

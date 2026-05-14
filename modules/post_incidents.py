from typing import Any

import httpx

from modules.fetch_thread_list import BACKEND_BASE_URL
from modules.progress_log import describe_payload, log_step


MATHRUBHUMI_BASE_URL = "https://www.mathrubhumi.com"


def post_final_gold_incidents(final_gold_data: Any, base_url: str = BACKEND_BASE_URL) -> list[Any]:
    """Post each incident from final_gold_data['final_response'] to the backend."""
    incidents = _extract_incidents(final_gold_data)
    url = f"{base_url.rstrip('/')}/incidents"
    responses: list[Any] = []

    log_step(f"Preparing to post {len(incidents)} incident(s) to {url}.")
    for index, incident in enumerate(incidents, start=1):
        payload = _build_incident_payload(incident)
        log_step(
            "Posting incident "
            f"{index}/{len(incidents)} with thread_id={payload['thread_id']!r}."
        )
        response = httpx.post(url, json=payload, timeout=None)
        log_step(
            "Received incident POST response "
            f"{response.status_code} for item {index}/{len(incidents)}."
        )
        response.raise_for_status()
        parsed_response = _parse_response_body(response)
        responses.append(parsed_response)
        log_step(
            "Stored incident POST response payload "
            f"{describe_payload(parsed_response)} for item {index}/{len(incidents)}."
        )

    log_step(f"Completed posting {len(responses)} incident(s) to {url}.")
    return responses


def _extract_incidents(final_gold_data: Any) -> list[dict[str, Any]]:
    if not isinstance(final_gold_data, dict):
        raise ValueError("final_gold_data must be a dict containing final_response.")

    final_response = final_gold_data.get("final_response")
    if final_response is None:
        log_step("No final_response found in final_gold_data; skipping incident posting.")
        return []

    if not isinstance(final_response, list):
        raise ValueError("final_response must be a list of incident payloads.")

    log_step(f"Extracted {len(final_response)} incident candidate(s) from final_response.")
    return final_response


def _build_incident_payload(incident: Any) -> dict[str, Any]:
    if not isinstance(incident, dict):
        raise ValueError("Each final_response item must be a dict.")

    thread_id = incident.get("thread_id")
    body = incident.get("body")
    source_url = incident.get("source_url")
    persons_involved = incident.get("persons_involved")

    if thread_id in (None, ""):
        raise ValueError("Incident payload is missing thread_id.")
    if not isinstance(body, str) or not body.strip():
        raise ValueError("Incident payload is missing body.")
    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError("Incident payload is missing source_url.")
    if persons_involved is None:
        persons_involved = []
    if not isinstance(persons_involved, list):
        raise ValueError("Incident payload persons_involved must be a list.")

    payload = {
        "thread_id": thread_id,
        "body": body.strip(),
        "source_url": _normalize_source_url(source_url.strip()),
        "persons_involved": persons_involved,
    }
    log_step(f"Built incident payload {describe_payload(payload)}.")
    return payload


def _normalize_source_url(source_url: str) -> str:
    if source_url.startswith(("http://", "https://")):
        return source_url

    normalized_url = f"{MATHRUBHUMI_BASE_URL}{source_url}"
    log_step(f"Normalized relative source_url to {normalized_url}.")
    return normalized_url


def _parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text = response.text.strip()
        return text or None

from typing import Any

import httpx

from modules.fetch_thread_list import BACKEND_BASE_URL


MATHRUBHUMI_BASE_URL = "https://www.mathrubhumi.com"


def post_final_gold_incidents(final_gold_data: Any, base_url: str = BACKEND_BASE_URL) -> list[Any]:
    """Post each incident from final_gold_data['normalized_incidents'] to the backend."""
    incidents = _extract_incidents(final_gold_data)
    url = f"{base_url.rstrip('/')}/incidents"
    responses: list[Any] = []

    for incident in incidents:
        payload = _build_incident_payload(incident)
        response = httpx.post(url, json=payload, timeout=None)
        response.raise_for_status()
        parsed_response = _parse_response_body(response)
        responses.append(parsed_response)

    return responses


def _extract_incidents(final_gold_data: Any) -> list[dict[str, Any]]:
    if not isinstance(final_gold_data, dict):
        raise ValueError(
            "final_gold_data must be a dict containing normalized_incidents."
        )

    incidents = final_gold_data.get("normalized_incidents")
    if not isinstance(incidents, list):
        raise ValueError("normalized_incidents must be a list of incident payloads.")
    if not all(isinstance(item, dict) for item in incidents):
        raise ValueError("normalized_incidents must contain only incident objects.")

    return incidents


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
    return payload


def _normalize_source_url(source_url: str) -> str:
    if source_url.startswith(("http://", "https://")):
        return source_url

    return f"{MATHRUBHUMI_BASE_URL}{source_url}"


def _parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text = response.text.strip()
        return text or None

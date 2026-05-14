import json
from typing import Any

from modules.progress_log import describe_payload, log_step


def normalize_final_incidents(
    final_response: Any,
    final_response_raw_text: Any,
) -> list[dict[str, Any]]:
    """Normalize final-stage LLM output into a validated incident list."""
    payload = final_response
    payload_source = "final_response"

    if payload is None:
        log_step("final_response was None; attempting normalization from raw text.")
        payload = _parse_raw_text_payload(final_response_raw_text)
        payload_source = "final_response_raw_text"

    incidents = _normalize_incident_list(payload, payload_source)
    log_step(
        "Normalized final incidents successfully from "
        f"{payload_source} with {len(incidents)} item(s)."
    )
    return incidents


def _parse_raw_text_payload(raw_text: Any) -> Any:
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("final_response_raw_text was empty while final_response was missing.")

    for candidate in _json_candidates(raw_text):
        try:
            parsed = json.loads(candidate)
            log_step(
                "Parsed final_response_raw_text candidate as "
                f"{describe_payload(parsed)}."
            )
            return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError("final_response_raw_text did not contain parseable JSON.")


def _normalize_incident_list(payload: Any, payload_source: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError(
            f"{payload_source} must be a JSON array of incident objects, got "
            f"{describe_payload(payload)}."
        )

    normalized_incidents: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        normalized_incidents.append(_normalize_incident_item(item, index, payload_source))

    return normalized_incidents


def _normalize_incident_item(
    item: Any,
    index: int,
    payload_source: str,
) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(
            f"{payload_source}[{index}] must be an object, got {describe_payload(item)}."
        )

    thread_id = _normalize_int_like(
        item.get("thread_id"),
        f"{payload_source}[{index}].thread_id",
    )
    body = _normalize_required_text(
        item.get("body"),
        f"{payload_source}[{index}].body",
    )
    source_url = _normalize_required_text(
        item.get("source_url"),
        f"{payload_source}[{index}].source_url",
    )
    persons_involved = _normalize_person_ids(
        item.get("persons_involved", []),
        f"{payload_source}[{index}].persons_involved",
    )

    normalized_item = {
        "thread_id": thread_id,
        "body": body,
        "source_url": source_url,
        "persons_involved": persons_involved,
    }
    log_step(f"Normalized incident item {index} as {describe_payload(normalized_item)}.")
    return normalized_item


def _normalize_int_like(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer, not boolean.")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ValueError(f"{field_name} must be an integer or numeric string.")


def _normalize_required_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _normalize_person_ids(value: Any, field_name: str) -> list[int]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")

    normalized_ids: list[int] = []
    for index, item in enumerate(value, start=1):
        normalized_ids.append(_normalize_int_like(item, f"{field_name}[{index}]"))
    return normalized_ids


def _json_candidates(raw_text: str) -> list[str]:
    stripped_text = raw_text.strip()
    candidates = [stripped_text]

    if stripped_text.startswith("```") and stripped_text.endswith("```"):
        fence_lines = stripped_text.splitlines()
        if len(fence_lines) >= 3:
            candidates.append("\n".join(fence_lines[1:-1]).strip())

    for opening, closing in (("{", "}"), ("[", "]")):
        start = stripped_text.find(opening)
        end = stripped_text.rfind(closing)
        if start != -1 and end != -1 and end > start:
            candidates.append(stripped_text[start : end + 1])

    return candidates

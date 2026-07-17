import json
from pathlib import Path
from typing import Any

from modules.confidence_checker import confidence_checker
from modules.llm_node import llm_node
from modules.match_threads import match_threads
from modules.prompt_loader import load_prompt
from modules.providers import generate_gemini_embedding
from modules.vector_waiting_list_incidents import vector_waiting_list_incidents


GOLD_TRANSLATION_PROMPT = "prompt_translate.txt"
GOLD_CLASSIFIER_PROMPT = "isPolitical_classifier_prompt.txt"
WAITING_LIST_CLASSIFICATION_PROMPT = "waiting_list_classification_prompt.txt"
WAITING_LIST_THREAD_PROMPT = "waiting_list_thread_prompt.txt"

PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"


def _required_waiting_list_matches() -> int:
    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    return int(params["required_waiting_list_matches"])
WAITING_LIST_CLASSIFICATION_TEXT_LIMIT = 240
GOLD_SILVER_KEYS = [
    "itemTitle",
    "itemTitleLead",
    "relatedStoriesTopic",
    "content",
    "source_id",
    "source_url",
]


def _build_translation_prompt(silver_item: dict[str, Any]) -> str:
    prompt = load_prompt(GOLD_TRANSLATION_PROMPT)
    silver_item_json = json.dumps(silver_item, ensure_ascii=False, indent=2)
    return f"{prompt}\n\nsilver_level_item:\n{silver_item_json}"


def _build_classifier_prompt(gold_items: list[dict[str, Any]]) -> str:
    prompt = load_prompt(GOLD_CLASSIFIER_PROMPT)
    gold_items_json = json.dumps(gold_items, ensure_ascii=False, indent=2)
    return f"{prompt}\n\ngold_level_items:\n{gold_items_json}"


def _build_waiting_list_classification_prompt(waiting_list_items: list[dict[str, Any]]) -> str:
    prompt = load_prompt(WAITING_LIST_CLASSIFICATION_PROMPT)
    waiting_list_items_json = json.dumps(waiting_list_items, ensure_ascii=False, indent=2)
    return f"{prompt}\n\nwaiting_list_items:\n{waiting_list_items_json}"


def _truncate_waiting_list_text(text: Any) -> Any:
    if not isinstance(text, str) or len(text) <= WAITING_LIST_CLASSIFICATION_TEXT_LIMIT:
        return text

    return f"{text[:WAITING_LIST_CLASSIFICATION_TEXT_LIMIT]}...[truncated]"


def _build_slim_waiting_list_classification_items(waiting_list_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slim_waiting_list_items: list[dict[str, Any]] = []
    for waiting_list_item in waiting_list_items:
        slim_incident_list: list[dict[str, Any]] = []
        for incident in waiting_list_item.get("incidentList", [])[:2]:
            if not isinstance(incident, dict):
                continue

            # The score is deliberately withheld: the model judges relatedness,
            # the cosine score is supplied by Postgres.
            slim_incident_list.append(
                {
                    "id": incident.get("id"),
                    "content": _truncate_waiting_list_text(incident.get("content")),
                }
            )

        slim_waiting_list_items.append(
            {
                "para_content": _truncate_waiting_list_text(waiting_list_item.get("para_content")),
                "source_id": waiting_list_item.get("source_id", waiting_list_item.get("sourceid")),
                "incidentList": slim_incident_list,
            }
        )

    return slim_waiting_list_items


def _build_waiting_list_classification_lookup(
    waiting_list_items: list[dict[str, Any]],
) -> dict[Any, dict[str, Any]]:
    waiting_list_lookup: dict[Any, dict[str, Any]] = {}
    for waiting_list_item in waiting_list_items:
        incident_lookup: dict[Any, dict[str, Any]] = {}
        for incident in waiting_list_item.get("incidentList", []):
            if not isinstance(incident, dict):
                continue

            incident_lookup[incident.get("id")] = {
                "content": incident.get("content"),
                "source_url": incident.get("source_url"),
                "source_id": incident.get("source_id"),
                "confidence_score": incident.get("confidence_score"),
            }

        waiting_list_lookup[waiting_list_item.get("source_id", waiting_list_item.get("sourceid"))] = {
            "para_content": waiting_list_item.get("para_content"),
            "vector": waiting_list_item.get("vector"),
            "source_url": waiting_list_item.get("source_url"),
            "incident_lookup": incident_lookup,
        }

    return waiting_list_lookup


def _build_waiting_list_thread_prompt(waiting_list_items: list[dict[str, Any]]) -> str:
    prompt = load_prompt(WAITING_LIST_THREAD_PROMPT)
    waiting_list_items_json = json.dumps(waiting_list_items, ensure_ascii=False, indent=2)
    return f"{prompt}\n\nwaiting_list_items:\n{waiting_list_items_json}"


def _parse_json_response(response_text: str) -> dict[str, Any]:
    normalized_text = response_text.strip()
    if normalized_text.startswith("```"):
        normalized_text = normalized_text.removeprefix("```json").removeprefix("```").strip()
        if normalized_text.endswith("```"):
            normalized_text = normalized_text[:-3].strip()

    return json.loads(normalized_text)


def _translate_silver_item(silver_item: dict[str, Any]) -> dict[str, Any]:
    translation_response = llm_node(prompt=_build_translation_prompt(silver_item))
    return _parse_json_response(translation_response)


def _build_embedding_input(translated_item: dict[str, Any]) -> dict[str, Any]:
    embedding_input = dict(translated_item)
    embedding_input.pop("source_id", None)
    return embedding_input


def _build_silver_lookup(silver_level_data: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    silver_lookup: dict[str, dict[str, Any]] = {}
    for silver_item in silver_level_data:
        silver_lookup[silver_item["source_id"]] = {key: silver_item[key] for key in GOLD_SILVER_KEYS if key in silver_item}

    return silver_lookup


def _enrich_compared_data(
    compared_data: list[dict[str, Any]],
    silver_lookup: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched_data: list[dict[str, Any]] = []
    for compared_item in compared_data:
        source_id = compared_item["source_id"]
        enriched_item = dict(compared_item)
        enriched_item.update(silver_lookup.get(source_id, {}))
        enriched_data.append(enriched_item)

    return enriched_data


def _coerce_thread_id(thread_id: Any) -> Any:
    if isinstance(thread_id, bool) or thread_id is None:
        return None
    if isinstance(thread_id, int):
        return thread_id
    if isinstance(thread_id, str) and thread_id.strip().isdigit():
        return int(thread_id.strip())

    return None


def _normalize_classifier_response(
    classifier_payload: dict[str, Any],
    source_url_lookup: dict[Any, Any],
    thread_score_lookup: dict[Any, dict[Any, float]],
) -> dict[str, Any]:
    political_items: list[dict[str, Any]] = []
    for item in classifier_payload.get("political", []):
        if not isinstance(item, dict):
            continue

        source_id = item.get("source_id")
        thread_id = _coerce_thread_id(item.get("thread_id"))
        # The model picks which thread; the cosine score for that thread decides
        # whether it is good enough. A thread the model invented has no score and
        # is rejected rather than trusted.
        confidence_level = thread_score_lookup.get(source_id, {}).get(thread_id)
        political_item = {
            "para_content": item.get("para_content"),
            "source_id": source_id,
            "thread_id": thread_id if confidence_level is not None else None,
            "confidence_level": confidence_level,
        }
        source_url = source_url_lookup.get(source_id)
        if source_url is not None:
            political_item["source_url"] = source_url
        political_items.append(political_item)

    non_political_items: list[str] = []
    for item in classifier_payload.get("non-political", classifier_payload.get("non_political", [])):
        if isinstance(item, str):
            non_political_items.append(item)
        elif isinstance(item, dict) and "source_id" in item:
            non_political_items.append(item["source_id"])

    return {
        "political": political_items,
        "non-political": non_political_items,
    }


def _build_thread_score_lookup(gold_items: list[dict[str, Any]]) -> dict[Any, dict[Any, float]]:
    thread_score_lookup: dict[Any, dict[Any, float]] = {}
    for item in gold_items:
        thread_score_lookup[item.get("source_id")] = {
            thread["thread_id"]: thread["scores"] for thread in item.get("Threads", [])
        }

    return thread_score_lookup


def _classify_gold_items(gold_items: list[dict[str, Any]]) -> dict[str, Any]:
    classifier_response = llm_node(prompt=_build_classifier_prompt(gold_items))
    classifier_payload = _parse_json_response(classifier_response)
    source_url_lookup = {item.get("source_id"): item.get("source_url") for item in gold_items}
    return _normalize_classifier_response(
        classifier_payload,
        source_url_lookup,
        _build_thread_score_lookup(gold_items),
    )


def _coerce_confidence_score(*candidates: Any) -> float:
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            return float(candidate)
        except (TypeError, ValueError):
            continue

    return 0.0


def _is_related(incident: dict[str, Any]) -> bool:
    """The model's semantic verdict. Anything unparseable counts as unrelated."""
    return incident.get("is_related") is True


def _normalize_waiting_list_classification_response(
    classifier_payload: Any,
    waiting_list_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    waiting_list_lookup = _build_waiting_list_classification_lookup(waiting_list_items)
    if isinstance(classifier_payload, list):
        classified_waiting_list_items = classifier_payload
    elif isinstance(classifier_payload, dict):
        classified_waiting_list_items = classifier_payload.get(
            "waiting_list_items",
            classifier_payload.get("data", classifier_payload.get("items", [])),
        )
        if not isinstance(classified_waiting_list_items, list):
            classified_waiting_list_items = [classified_waiting_list_items]
    else:
        classified_waiting_list_items = []

    normalized_items: list[dict[str, Any]] = []
    for item in classified_waiting_list_items:
        if not isinstance(item, dict):
            continue

        source_id = item.get("source_id", item.get("sourceid"))
        original_waiting_list_item = waiting_list_lookup.get(source_id, {})
        incident_lookup = original_waiting_list_item.get("incident_lookup", {})
        normalized_incidents: list[dict[str, Any]] = []
        for incident in item.get("incidentList", []):
            if not isinstance(incident, dict):
                continue

            # Both must agree: the model says it is the same story, and the
            # cosine score decides how strongly. The model never supplies the
            # number -- it used to invent one, and that invented float was what
            # gated thread creation.
            if not _is_related(incident):
                continue

            incident_id = incident.get("id")
            original_incident = incident_lookup.get(incident_id, {})
            normalized_incident = {
                "id": incident_id,
                "content": original_incident.get("content", incident.get("content")),
                "confidence_score": _coerce_confidence_score(
                    original_incident.get("confidence_score"),
                ),
            }
            incident_source_url = original_incident.get("source_url", incident.get("source_url"))
            if incident_source_url is not None:
                normalized_incident["source_url"] = incident_source_url
            incident_source_id = original_incident.get("source_id")
            if incident_source_id is not None:
                normalized_incident["source_id"] = incident_source_id
            normalized_incidents.append(normalized_incident)

        normalized_incidents.sort(key=lambda incident: incident["confidence_score"], reverse=True)

        normalized_item = {
            "para_content": original_waiting_list_item.get("para_content", item.get("para_content")),
            "source_id": source_id,
            "vector": original_waiting_list_item.get("vector", item.get("vector")),
            "incidentList": normalized_incidents[:_required_waiting_list_matches()],
        }
        source_url = original_waiting_list_item.get("source_url", item.get("source_url"))
        if source_url is not None:
            normalized_item["source_url"] = source_url
        normalized_items.append(normalized_item)

    return normalized_items


def _classify_waiting_list_items(waiting_list_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slim_waiting_list_items = _build_slim_waiting_list_classification_items(waiting_list_items)
    classifier_response = llm_node(prompt=_build_waiting_list_classification_prompt(slim_waiting_list_items))
    classifier_payload = _parse_json_response(classifier_response)
    return _normalize_waiting_list_classification_response(classifier_payload, waiting_list_items)


def _extract_political_items(classifier_payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(classifier_payload.get("political", []))


def _attach_vectors_to_political_items(
    political_items: list[dict[str, Any]],
    vector_lookup: dict[str, Any],
) -> list[dict[str, Any]]:
    enriched_political_items: list[dict[str, Any]] = []
    for political_item in political_items:
        enriched_political_item = dict(political_item)
        source_id = political_item.get("source_id")
        if source_id in vector_lookup:
            enriched_political_item["vector"] = vector_lookup[source_id]
        enriched_political_items.append(enriched_political_item)

    return enriched_political_items


def _reshape_political_items_for_thread_output(political_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reshaped_items: list[dict[str, Any]] = []
    for political_item in political_items:
        reshaped_item = {
            "source_id": political_item.get("source_id"),
            "thread_id": political_item.get("thread_id"),
            "content": political_item.get("para_content"),
        }
        if political_item.get("source_url") is not None:
            reshaped_item["source_url"] = political_item["source_url"]
        reshaped_items.append(reshaped_item)

    return reshaped_items


def _build_gold_output_wrapper(
    main_output: list[dict[str, Any]],
    secondary_output: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    combined_output = main_output + secondary_output
    return {
        "main_output": main_output,
        "secondary_output": secondary_output,
        "combined": combined_output,
    }


def build_gold_level_data(silver_level_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Translate silver items, embed them, match them to threads, and classify the final records."""
    gold_level_data: list[dict[str, Any]] = []
    main_output: list[dict[str, Any]] = []
    secondary_output: list[dict[str, Any]] = []
    print(
        f"DEBUG: Gold input count = {len(silver_level_data)}; "
        f"source IDs = {[item['source_id'] for item in silver_level_data]}"
    )

    for silver_item in silver_level_data:
        translated_item = _translate_silver_item(silver_item)
        embedding_input = _build_embedding_input(translated_item)
        vector = generate_gemini_embedding(embedding_input)
        gold_level_data.append(
            {
                "source_id": silver_item["source_id"],
                "vector": vector,
            }
        )

    print(
        f"DEBUG: Gold embedded count = {len(gold_level_data)}; "
        f"source IDs = {[item['source_id'] for item in gold_level_data]}"
    )

    # Postgres ranks the threads; no thread vector crosses the wire.
    compared_data = [
        {**item, "Threads": match_threads(item["vector"])} for item in gold_level_data
    ]
    silver_lookup = _build_silver_lookup(silver_level_data)
    enriched_data = _enrich_compared_data(compared_data, silver_lookup)
    classified_data = _classify_gold_items(enriched_data)
    non_political_source_ids = list(classified_data.get("non-political", []))
    vector_lookup = {item["source_id"]: item["vector"] for item in gold_level_data}
    political_items = _attach_vectors_to_political_items(
        _extract_political_items(classified_data),
        vector_lookup,
    )
    print(
        f"DEBUG: Gold classified political count = {len(political_items)}; "
        f"source IDs = {[item.get('source_id') for item in political_items]}"
    )
    print(
        f"DEBUG: Gold classified non-political count = {len(non_political_source_ids)}; "
        f"source IDs = {non_political_source_ids}"
    )

    passed_items: list[dict[str, Any]] = []
    failed_political_items: list[dict[str, Any]] = []
    for political_item in political_items:
        if confidence_checker([political_item]):
            passed_items.append(political_item)
        else:
            failed_political_items.append(political_item)

    print(
        f"DEBUG: Gold confidence-passed count = {len(passed_items)}; "
        f"source IDs = {[item.get('source_id') for item in passed_items]}"
    )
    print(
        f"DEBUG: Gold confidence-failed count = {len(failed_political_items)}; "
        f"source IDs = {[item.get('source_id') for item in failed_political_items]}"
    )
    main_output = _reshape_political_items_for_thread_output(passed_items)

    if failed_political_items:
        failed_items: list[dict[str, Any]] = []
        for political_item in failed_political_items:
            vector_ref = political_item.get("vector")
            if vector_ref is None:
                continue

            # Already carries content, source_url and the cosine score.
            incident_list = vector_waiting_list_incidents(vector_ref)

            failed_item = {
                "para_content": political_item["para_content"],
                "source_id": political_item["source_id"],
                "incidentList": incident_list,
                "vector": vector_ref,
            }
            if political_item.get("source_url") is not None:
                failed_item["source_url"] = political_item["source_url"]
            failed_items.append(failed_item)

        if failed_items:
            secondary_output = _classify_waiting_list_items(failed_items)

    print(
        f"DEBUG: Gold main output count = {len(main_output)}; "
        f"source IDs = {[item.get('source_id') for item in main_output]}"
    )
    print(
        f"DEBUG: Gold secondary output count = {len(secondary_output)}; "
        f"source IDs = {[item.get('source_id') for item in secondary_output]}"
    )
    gold_output = _build_gold_output_wrapper(main_output, secondary_output)
    gold_output["non_political_source_ids"] = non_political_source_ids
    return gold_output

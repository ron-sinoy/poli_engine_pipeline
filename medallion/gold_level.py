import json
from typing import Any

from modules.compare_vectors import build_compare_vectors_data
from modules.confidence_checker import confidence_checker
from modules.fetch_api import fetch_api
from modules.content_waiting_list_incidents import content_waiting_list_incidents
from modules.llm_node import llm_node
from modules.prompt_loader import load_prompt
from modules.post_threads import post_threads
from modules.post_waitinglists import post_waitinglists
from modules.providers import generate_gemini_embedding
from modules.update_db import update_db
from modules.vector_waiting_list_incidents import vector_waiting_list_incidents
from modules.waiting_list_confidence_checker import waiting_list_confidence_checker


GOLD_TRANSLATION_PROMPT = "prompt_translate.txt"
GOLD_CLASSIFIER_PROMPT = "isPolitical_classifier_prompt.txt"
WAITING_LIST_CLASSIFICATION_PROMPT = "waiting_list_classification_prompt.txt"
WAITING_LIST_THREAD_PROMPT = "waiting_list_thread_prompt.txt"
THREADS_INTERNAL_URL = "https://poli-engine-backend-production.up.railway.app/threadsInternal"
GOLD_SILVER_KEYS = [
    "itemTitle",
    "itemTitleLead",
    "relatedStoriesTopic",
    "content",
    "source_id",
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


def _fetch_threads_internal() -> list[dict[str, Any]]:
    threads_internal = fetch_api(THREADS_INTERNAL_URL)
    if isinstance(threads_internal, dict):
        return threads_internal.get("threadsInternal", threads_internal.get("data", []))

    return threads_internal


def _build_threads_vectors_list(threads_internal: list[dict[str, Any]]) -> list[dict[str, Any]]:
    threads_vectors_list: list[dict[str, Any]] = []
    for thread_item in threads_internal:
        threads_vectors_list.append(
            {
                "thread_id": thread_item["thread_id"],
                "title": thread_item["title"],
                "summary": thread_item["summary"],
                "thread_vectors": thread_item.get("thread_vectors", thread_item.get("vectors", [])),
            }
        )

    return threads_vectors_list


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


def _normalize_classifier_response(classifier_payload: dict[str, Any]) -> dict[str, Any]:
    political_items: list[dict[str, Any]] = []
    for item in classifier_payload.get("political", []):
        if not isinstance(item, dict):
            continue

        political_items.append(
            {
                "para_content": item.get("para_content"),
                "source_id": item.get("source_id"),
                "thread_id": item.get("thread_id"),
                "confidence_level": item.get("confidence_level"),
            }
        )

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


def _classify_gold_items(gold_items: list[dict[str, Any]]) -> dict[str, Any]:
    classifier_response = llm_node(prompt=_build_classifier_prompt(gold_items))
    classifier_payload = _parse_json_response(classifier_response)
    return _normalize_classifier_response(classifier_payload)


def _normalize_waiting_list_incident(incident: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": incident.get("id"),
        "content": incident.get("content"),
        "confidence_score": float(incident.get("confidence_score", 0.0)),
    }


def _normalize_waiting_list_classification_response(
    classifier_payload: Any,
) -> list[dict[str, Any]]:
    if isinstance(classifier_payload, list):
        waiting_list_items = classifier_payload
    elif isinstance(classifier_payload, dict):
        waiting_list_items = classifier_payload.get(
            "waiting_list_items",
            classifier_payload.get("data", classifier_payload.get("items", [])),
        )
        if not isinstance(waiting_list_items, list):
            waiting_list_items = [waiting_list_items]
    else:
        waiting_list_items = []

    normalized_items: list[dict[str, Any]] = []
    for item in waiting_list_items:
        if not isinstance(item, dict):
            continue

        normalized_incidents = [
            _normalize_waiting_list_incident(incident)
            for incident in item.get("incidentList", [])
            if isinstance(incident, dict)
        ]
        normalized_incidents.sort(key=lambda incident: incident["confidence_score"], reverse=True)

        normalized_items.append(
            {
                "para_content": item.get("para_content"),
                "source_id": item.get("source_id", item.get("sourceid")),
                "vector": item.get("vector"),
                "incidentList": normalized_incidents[:2],
            }
        )

    return normalized_items


def _classify_waiting_list_items(waiting_list_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    classifier_response = llm_node(prompt=_build_waiting_list_classification_prompt(waiting_list_items))
    classifier_payload = _parse_json_response(classifier_response)
    return _normalize_waiting_list_classification_response(classifier_payload)


def _reshape_waiting_list_item_for_thread_creation(waiting_list_item: dict[str, Any]) -> list[dict[str, Any]]:
    thread_candidates = [
        {
            "source_id": waiting_list_item["source_id"],
            "content": waiting_list_item["para_content"],
            "thread_id": None,
        }
    ]

    for incident in waiting_list_item.get("incidentList", [])[:2]:
        thread_candidates.append(
            {
                "source_id": incident["id"],
                "content": incident["content"],
                "thread_id": None,
            }
        )

    return thread_candidates


def _normalize_waiting_list_thread_response(thread_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": thread_payload.get("title"),
        "summary": thread_payload.get("summary"),
    }


def _generate_waiting_list_thread_metadata(waiting_list_items: list[dict[str, Any]]) -> dict[str, Any]:
    thread_response = llm_node(prompt=_build_waiting_list_thread_prompt(waiting_list_items))
    thread_payload = _parse_json_response(thread_response)
    return _normalize_waiting_list_thread_response(thread_payload)


def _attach_thread_ids(
    waiting_list_items: list[dict[str, Any]],
    thread_id: Any,
) -> list[dict[str, Any]]:
    enriched_waiting_list_items: list[dict[str, Any]] = []
    for waiting_list_item in waiting_list_items:
        enriched_waiting_list_item = dict(waiting_list_item)
        enriched_waiting_list_item["thread_id"] = thread_id
        enriched_waiting_list_items.append(enriched_waiting_list_item)

    return enriched_waiting_list_items


def _create_threads_from_waiting_list_item(waiting_list_item: dict[str, Any]) -> list[dict[str, Any]]:
    thread_candidates = _reshape_waiting_list_item_for_thread_creation(waiting_list_item)
    thread_metadata = _generate_waiting_list_thread_metadata(thread_candidates)
    generate_gemini_embedding(
        {
            "title": thread_metadata["title"],
            "summary": thread_metadata["summary"],
        }
    )
    thread_id = post_threads(thread_metadata["title"], thread_metadata["summary"])
    return _attach_thread_ids(thread_candidates, thread_id)


def _update_non_political_source_ids(classifier_payload: dict[str, Any]) -> None:
    for source_id in classifier_payload.get("non-political", []):
        update_db(source_id, "filtered")


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
        reshaped_items.append(
            {
                "source_id": political_item.get("source_id"),
                "thread_id": political_item.get("thread_id"),
                "content": political_item.get("para_content"),
            }
        )

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


def _build_waiting_list_content_lookup(waiting_list_content: list[dict[str, Any]]) -> dict[Any, Any]:
    content_lookup: dict[Any, Any] = {}
    for waiting_list_item in waiting_list_content:
        content_lookup[waiting_list_item["id"]] = waiting_list_item.get("content")

    return content_lookup


def _enrich_failed_items_with_content(
    failed_items: list[dict[str, Any]],
    content_lookup: dict[Any, Any],
) -> list[dict[str, Any]]:
    enriched_failed_items: list[dict[str, Any]] = []
    for failed_item in failed_items:
        incident_list: list[dict[str, Any]] = []
        for incident in failed_item.get("incidentList", []):
            incident_list.append(
                {
                    "id": incident["id"],
                    "content": content_lookup.get(incident["id"]),
                }
            )

        enriched_failed_item = dict(failed_item)
        enriched_failed_item["incidentList"] = incident_list
        enriched_failed_items.append(enriched_failed_item)

    return enriched_failed_items


def build_gold_level_data(silver_level_data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Translate silver items, embed them, match them to threads, and classify the final records."""
    gold_level_data: list[dict[str, Any]] = []
    main_output: list[dict[str, Any]] = []
    secondary_output: list[dict[str, Any]] = []
    threads_internal = _fetch_threads_internal()
    threads_vectors_list = _build_threads_vectors_list(threads_internal)

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

    compared_data = build_compare_vectors_data(gold_level_data, threads_vectors_list)
    silver_lookup = _build_silver_lookup(silver_level_data)
    enriched_data = _enrich_compared_data(compared_data, silver_lookup)
    classified_data = _classify_gold_items(enriched_data)
    _update_non_political_source_ids(classified_data)
    vector_lookup = {item["source_id"]: item["vector"] for item in gold_level_data}
    political_items = _attach_vectors_to_political_items(
        _extract_political_items(classified_data),
        vector_lookup,
    )

    if confidence_checker(political_items):
        main_output = _reshape_political_items_for_thread_output(political_items)
    else:
        waiting_list_content_lookup = _build_waiting_list_content_lookup(content_waiting_list_incidents())
        failed_items: list[dict[str, Any]] = []
        for political_item in political_items:
            vector_ref = political_item.get("vector")
            if vector_ref is None:
                continue

            incident_list = vector_waiting_list_incidents(vector_ref)

            failed_items.append(
                {
                    "para_content": political_item["para_content"],
                    "source_id": political_item["source_id"],
                    "incidentList": incident_list,
                    "vector": vector_ref,
                }
            )

        enriched_failed_items = _enrich_failed_items_with_content(failed_items, waiting_list_content_lookup)
        classified_waiting_list_items = _classify_waiting_list_items(enriched_failed_items)
        for waiting_list_item in classified_waiting_list_items:
            if waiting_list_confidence_checker([waiting_list_item]):
                secondary_output.extend(_create_threads_from_waiting_list_item(waiting_list_item))
            else:
                post_waitinglists(waiting_list_item["para_content"], waiting_list_item["vector"])

    return _build_gold_output_wrapper(main_output, secondary_output)

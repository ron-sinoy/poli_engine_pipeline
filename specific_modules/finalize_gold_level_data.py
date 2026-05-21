import json
from pathlib import Path
from typing import Any

from modules.fetch_thread_list import fetch_cache, fetch_thread_by_id
from modules.generate_llm_response import generate_llm_response
from modules.normalize_final_incidents import normalize_final_incidents
from modules.read_text_file import read_text_file


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PROMPT2_PATH = WORKSPACE_ROOT / "prompts" / "prompt2.txt"


def finalize_gold_level_data(
    initial_classification_gold_data: Any,
) -> dict[str, Any]:
    """Run the second gold-stage prompt with full initial payload, threads, and cache."""
    cache_payload = fetch_cache()
    prompt_template = read_text_file(PROMPT2_PATH)
    thread_details = _fetch_thread_details(initial_classification_gold_data)
    llm_result = generate_llm_response(
        _build_prompt(
            prompt_template,
            initial_classification_gold_data,
            thread_details,
            cache_payload,
        )
    )
    final_response = llm_result.get("parsed_json")
    final_response_raw_text = llm_result.get("raw_text", "")
    normalized_incidents = normalize_final_incidents(
        final_response,
        final_response_raw_text,
    )

    return {
        "initial_classification_gold_data": initial_classification_gold_data,
        "thread_details": thread_details,
        "cache_snapshot": cache_payload,
        "final_response": final_response,
        "final_response_raw_text": final_response_raw_text,
        "normalized_incidents": normalized_incidents,
    }


def _extract_thread_ids(initial_classification_gold_data: Any) -> list[Any]:
    if isinstance(initial_classification_gold_data, dict):
        thread_ids = initial_classification_gold_data.get("thread_ids")
        if isinstance(thread_ids, list):
            return thread_ids

        classification = initial_classification_gold_data.get("classification")
        if classification is not None:
            collected_ids: list[Any] = []
            _collect_thread_ids(classification, collected_ids)
            return collected_ids

    return []


def _fetch_thread_details(initial_classification_gold_data: Any) -> dict[str, Any]:
    thread_details: dict[str, Any] = {}
    for thread_id in _extract_thread_ids(initial_classification_gold_data):
        thread_details[str(thread_id)] = fetch_thread_by_id(thread_id)

    return thread_details


def _collect_thread_ids(classification: Any, collected_ids: list[Any]) -> None:
    if isinstance(classification, dict):
        if "thread_id" in classification:
            thread_id = classification["thread_id"]
            if thread_id not in collected_ids:
                collected_ids.append(thread_id)

        for value in classification.values():
            _collect_thread_ids(value, collected_ids)

    elif isinstance(classification, list):
        for item in classification:
            _collect_thread_ids(item, collected_ids)


def _build_prompt(
    prompt_template: str,
    initial_classification_gold_data: Any,
    thread_details: Any,
    cache_payload: Any,
) -> str:
    prompt_sections = [prompt_template.strip()]
    prompt_sections.append(
        _json_block("initial_classification_gold_data", initial_classification_gold_data)
    )
    prompt_sections.append(_json_block("thread_details", thread_details))
    prompt_sections.append(_json_block("cache", cache_payload))
    return "\n\n".join(section for section in prompt_sections if section)


def _json_block(label: str, payload: Any) -> str:
    return f"{label}:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"

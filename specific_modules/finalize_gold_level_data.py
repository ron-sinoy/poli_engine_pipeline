import json
from pathlib import Path
from typing import Any

from modules.fetch_thread_list import fetch_cache, fetch_thread_by_id
from modules.generate_llm_response import generate_llm_response
from modules.progress_log import describe_payload, log_step
from modules.read_text_file import read_text_file


PROMPT2_PATH = Path("prompts/prompt2.txt")


def finalize_gold_level_data(
    initial_classification_gold_data: Any,
) -> dict[str, Any]:
    """Run the second gold-stage prompt with full initial payload, threads, and cache."""
    log_step("Starting final gold data preparation.")
    cache_payload = fetch_cache()
    prompt_template = read_text_file(PROMPT2_PATH)
    thread_details = _fetch_thread_details(initial_classification_gold_data)
    log_step(
        "Running second gold LLM call with initial data "
        f"{describe_payload(initial_classification_gold_data)}, thread details "
        f"{describe_payload(thread_details)}, and cache "
        f"{describe_payload(cache_payload)}."
    )
    llm_result = generate_llm_response(
        _build_prompt(
            prompt_template,
            initial_classification_gold_data,
            thread_details,
            cache_payload,
        )
    )
    log_step(
        "Second gold LLM call completed with final response "
        f"{describe_payload(llm_result.get('parsed_json'))}."
    )

    return {
        "initial_classification_gold_data": initial_classification_gold_data,
        "thread_details": thread_details,
        "cache_snapshot": cache_payload,
        "final_response": llm_result.get("parsed_json"),
        "final_response_raw_text": llm_result.get("raw_text", ""),
    }


def _extract_thread_ids(initial_classification_gold_data: Any) -> list[Any]:
    if isinstance(initial_classification_gold_data, dict):
        thread_ids = initial_classification_gold_data.get("thread_ids")
        if isinstance(thread_ids, list):
            log_step(f"Using precomputed thread_ids list with {len(thread_ids)} item(s).")
            return thread_ids

        classification = initial_classification_gold_data.get("classification")
        if classification is not None:
            collected_ids: list[Any] = []
            _collect_thread_ids(classification, collected_ids)
            log_step(
                "Derived thread_ids from classification with "
                f"{len(collected_ids)} item(s)."
            )
            return collected_ids

    log_step("No thread ids were available for final gold stage.")
    return []


def _fetch_thread_details(initial_classification_gold_data: Any) -> dict[str, Any]:
    thread_details: dict[str, Any] = {}
    for thread_id in _extract_thread_ids(initial_classification_gold_data):
        log_step(f"Fetching thread details bundle entry for thread_id={thread_id!r}.")
        thread_details[str(thread_id)] = fetch_thread_by_id(thread_id)
        log_step(f"Stored thread details bundle entry for thread_id={thread_id!r}.")

    log_step(f"Collected thread details bundle {describe_payload(thread_details)}.")
    return thread_details


def _collect_thread_ids(classification: Any, collected_ids: list[Any]) -> None:
    if isinstance(classification, dict):
        if "thread_id" in classification:
            thread_id = classification["thread_id"]
            if thread_id not in collected_ids:
                collected_ids.append(thread_id)
                log_step(f"Captured final-stage thread_id={thread_id!r}.")

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
    prompt = "\n\n".join(section for section in prompt_sections if section)
    log_step(f"Built prompt2 payload with length {len(prompt)}.")
    return prompt


def _json_block(label: str, payload: Any) -> str:
    block = f"{label}:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    log_step(f"Created JSON block for {label} with length {len(block)}.")
    return block

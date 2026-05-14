import json
from pathlib import Path
from typing import Any

from modules.fetch_thread_list import fetch_threads_list
from modules.generate_llm_response import generate_llm_response
from modules.progress_log import describe_payload, log_step
from modules.read_text_file import read_text_file
from specific_modules.resolve_missing_threads import resolve_missing_threads


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PROMPT1_PATH = WORKSPACE_ROOT / "prompts" / "prompt1.txt"


def classify_gold_level_data(silver_level_data: Any) -> dict[str, Any]:
    """Classify the full silver-level dataset against the backend thread list."""
    log_step("Starting gold classification data preparation.")
    threads_list = fetch_threads_list()
    prompt_template = read_text_file(PROMPT1_PATH)
    log_step(
        "Running first gold LLM call with threads list "
        f"{describe_payload(threads_list)} and silver data "
        f"{describe_payload(silver_level_data)}."
    )
    llm_result = generate_llm_response(
        _build_prompt(prompt_template, threads_list, silver_level_data)
    )
    classification = llm_result.get("parsed_json")
    _validate_classification_payload(classification, llm_result.get("raw_text", ""))
    resolved_threads_list = threads_list
    created_threads: list[dict[str, Any]] = []
    resolution = resolve_missing_threads(
        classification,
        silver_level_data,
        threads_list,
    )
    classification = resolution["classification"]
    resolved_threads_list = resolution["threads_list"]
    created_threads = resolution["created_threads"]
    log_step(
        "First gold LLM call completed with classification "
        f"{describe_payload(classification)}."
    )

    return {
        "threads_list_snapshot": resolved_threads_list,
        "silver_level_data": silver_level_data,
        "created_threads": created_threads,
        "thread_ids": _extract_thread_ids(classification),
        "classification": classification,
        "classification_raw_text": llm_result.get("raw_text", ""),
    }


def _build_prompt(prompt_template: str, threads_list: Any, silver_level_data: Any) -> str:
    prompt_sections = [prompt_template.strip()]
    prompt_sections.append(_json_block("threads_list", threads_list))
    prompt_sections.append(_json_block("silver_level_data", silver_level_data))
    prompt = "\n\n".join(section for section in prompt_sections if section)
    log_step(f"Built prompt1 payload with length {len(prompt)}.")
    return prompt


def _json_block(label: str, payload: Any) -> str:
    block = f"{label}:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    log_step(f"Created JSON block for {label} with length {len(block)}.")
    return block


def _extract_thread_ids(classification: Any) -> list[Any]:
    collected_ids: list[Any] = []
    _collect_thread_ids(classification, collected_ids)
    log_step(f"Collected {len(collected_ids)} unique thread id(s) from classification.")
    return collected_ids


def _collect_thread_ids(classification: Any, collected_ids: list[Any]) -> None:
    if isinstance(classification, dict):
        if "thread_id" in classification:
            thread_id = classification["thread_id"]
            if thread_id not in collected_ids:
                collected_ids.append(thread_id)
                log_step(f"Captured thread_id={thread_id!r} from classification.")

        for value in classification.values():
            _collect_thread_ids(value, collected_ids)

    elif isinstance(classification, list):
        for item in classification:
            _collect_thread_ids(item, collected_ids)


def _validate_classification_payload(classification: Any, raw_text: str) -> None:
    if isinstance(classification, list):
        return

    raw_excerpt = raw_text.strip().replace("\n", " ")[:300]
    raise ValueError(
        "Prompt1 Gemini response did not parse into the expected JSON array. "
        f"Parsed shape: {describe_payload(classification)}. "
        f"Raw text excerpt: {raw_excerpt!r}"
    )

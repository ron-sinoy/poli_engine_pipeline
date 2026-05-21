import copy
import json
from pathlib import Path
from typing import Any

from modules.create_thread import create_thread, extract_thread_id
from modules.fetch_thread_list import fetch_threads_list
from modules.generate_llm_response import generate_llm_response
from modules.read_text_file import read_text_file


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
THREAD_METADATA_PROMPT_PATH = WORKSPACE_ROOT / "prompts" / "thread_metadata_prompt.txt"
NEW_THREAD_SENTINELS = {None, "", "NEW_THREAD", "new_thread", "new thread"}


def resolve_missing_threads(
    classification: Any,
    silver_level_data: Any,
    threads_list: Any,
) -> dict[str, Any]:
    """Create backend threads for unmatched classifications and rewrite their ids."""
    rewritten_classification = copy.deepcopy(classification)
    pending_items: list[dict[str, Any]] = []
    _collect_pending_items(rewritten_classification, pending_items)

    if not pending_items:
        return {
            "classification": rewritten_classification,
            "threads_list": threads_list,
            "created_threads": [],
        }

    prompt_template = read_text_file(THREAD_METADATA_PROMPT_PATH)
    silver_lookup = _build_silver_lookup(silver_level_data)
    created_threads: list[dict[str, Any]] = []

    for index, pending_item in enumerate(pending_items, start=1):
        source_item = _match_source_item(pending_item, silver_lookup)
        metadata_response = generate_llm_response(
            _build_thread_metadata_prompt(prompt_template, pending_item, source_item)
        )
        thread_payload = _extract_thread_payload(metadata_response.get("parsed_json"))
        created_thread_response = create_thread(
            thread_payload["title"],
            thread_payload["summary"],
        )
        created_thread_id = extract_thread_id(created_thread_response)
        pending_item["thread_id"] = created_thread_id
        created_threads.append(
            {
                "thread_id": created_thread_id,
                "contentID": pending_item.get("contentID"),
                "itemTitle": pending_item.get("itemTitle"),
                "title": thread_payload["title"],
                "summary": thread_payload["summary"],
            }
        )

    refreshed_threads_list = fetch_threads_list()
    return {
        "classification": rewritten_classification,
        "threads_list": refreshed_threads_list,
        "created_threads": created_threads,
    }


def _collect_pending_items(payload: Any, pending_items: list[dict[str, Any]]) -> None:
    if isinstance(payload, dict):
        if _needs_new_thread(payload):
            pending_items.append(payload)

        for value in payload.values():
            _collect_pending_items(value, pending_items)

    elif isinstance(payload, list):
        for item in payload:
            _collect_pending_items(item, pending_items)


def _needs_new_thread(classification_item: dict[str, Any]) -> bool:
    matched_existing_thread = classification_item.get("matched_existing_thread")
    if matched_existing_thread is False:
        return True

    thread_id = classification_item.get("thread_id")
    if thread_id in NEW_THREAD_SENTINELS:
        return True

    return False


def _build_silver_lookup(silver_level_data: Any) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    if not isinstance(silver_level_data, list):
        return lookup

    for item in silver_level_data:
        if not isinstance(item, dict):
            continue

        content_id = item.get("contentID")
        if isinstance(content_id, str) and content_id:
            lookup[f"contentID:{content_id}"] = item

        item_title = item.get("itemTitle")
        if isinstance(item_title, str) and item_title:
            lookup[f"itemTitle:{item_title}"] = item

    return lookup


def _match_source_item(
    classification_item: dict[str, Any],
    silver_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    content_id = classification_item.get("contentID")
    if isinstance(content_id, str) and content_id:
        matched = silver_lookup.get(f"contentID:{content_id}")
        if matched is not None:
            return matched

    item_title = classification_item.get("itemTitle")
    if isinstance(item_title, str) and item_title:
        matched = silver_lookup.get(f"itemTitle:{item_title}")
        if matched is not None:
            return matched

    return classification_item


def _build_thread_metadata_prompt(
    prompt_template: str,
    classification_item: dict[str, Any],
    source_item: dict[str, Any],
) -> str:
    prompt_sections = [prompt_template.strip()]
    prompt_sections.append(_json_block("classification_item", classification_item))
    prompt_sections.append(_json_block("source_item", source_item))
    return "\n\n".join(section for section in prompt_sections if section)


def _extract_thread_payload(parsed_json: Any) -> dict[str, str]:
    if not isinstance(parsed_json, dict):
        raise ValueError("Thread metadata response must be a JSON object.")

    title = parsed_json.get("title")
    summary = parsed_json.get("summary")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Thread metadata response is missing title.")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("Thread metadata response is missing summary.")

    payload = {
        "title": title.strip(),
        "summary": summary.strip(),
    }
    return payload


def _json_block(label: str, payload: Any) -> str:
    return f"{label}:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"

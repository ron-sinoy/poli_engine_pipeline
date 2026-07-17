import json
from pathlib import Path
from typing import Any

from modules.extract_persons import extract_persons, fetch_person_roster
from modules.llm_node import llm_node
from modules.post_incidents import post_incidents
from modules.post_threads import post_threads
from modules.post_waitinglists import post_waitinglists
from modules.prompt_loader import load_prompt
from modules.providers import generate_gemini_embedding
from modules.update_db import update_db
from modules.update_waitinglists import update_waitinglists
from modules.waiting_list_confidence_checker import waiting_list_confidence_checker


WAITING_LIST_THREAD_PROMPT = "waiting_list_thread_prompt.txt"
PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"


def _required_waiting_list_matches() -> int:
    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    return int(params["required_waiting_list_matches"])


def _parse_json_response(response_text: str) -> dict[str, Any]:
    normalized_text = response_text.strip()
    if normalized_text.startswith("```"):
        normalized_text = normalized_text.removeprefix("```json").removeprefix("```").strip()
        if normalized_text.endswith("```"):
            normalized_text = normalized_text[:-3].strip()

    return json.loads(normalized_text)


def _build_waiting_list_thread_prompt(waiting_list_items: list[dict[str, Any]]) -> str:
    prompt = load_prompt(WAITING_LIST_THREAD_PROMPT)
    waiting_list_items_json = json.dumps(waiting_list_items, ensure_ascii=False, indent=2)
    return f"{prompt}\n\nwaiting_list_items:\n{waiting_list_items_json}"


def _normalize_waiting_list_thread_response(thread_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": thread_payload.get("title"),
        "summary": thread_payload.get("summary"),
    }


def _generate_waiting_list_thread_metadata(waiting_list_items: list[dict[str, Any]]) -> dict[str, Any]:
    thread_response = llm_node(prompt=_build_waiting_list_thread_prompt(waiting_list_items))
    thread_payload = _parse_json_response(thread_response)
    return _normalize_waiting_list_thread_response(thread_payload)


def _reshape_waiting_list_item_for_thread_creation(waiting_list_item: dict[str, Any]) -> list[dict[str, Any]]:
    thread_candidates = [
        {
            "source_id": waiting_list_item["source_id"],
            "content": waiting_list_item["para_content"],
            "source_url": waiting_list_item.get("source_url"),
            "thread_id": None,
        }
    ]

    for incident in waiting_list_item.get("incidentList", [])[:_required_waiting_list_matches()]:
        thread_candidates.append(
            {
                "waiting_list_id": incident["id"],
                "source_id": incident.get("source_id"),
                "content": incident["content"],
                "source_url": incident.get("source_url"),
                "thread_id": None,
            }
        )

    return thread_candidates


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
    thread_vector = generate_gemini_embedding(
        {
            "title": thread_metadata["title"],
            "summary": thread_metadata["summary"],
        }
    )
    thread_id = post_threads(thread_metadata["title"], thread_metadata["summary"], thread_vector)
    return _attach_thread_ids(thread_candidates, thread_id)


def _post_incident_with_persons(
    thread_id: Any,
    content: str,
    source_url: Any,
    roster: list[dict[str, Any]],
) -> None:
    """The only way an incident reaches the backend.

    Every incident goes through here on both routing paths, so person links are
    recorded unconditionally rather than depending on which path was taken.
    """
    post_incidents(thread_id, content, source_url, extract_persons(content, roster))


def _post_incident_with_retry(
    thread_id: Any,
    content: str,
    source_url: Any,
    roster: list[dict[str, Any]],
    *,
    label: str,
) -> bool:
    """Try once, retry once on failure, then give up. Returns whether it posted."""
    for attempt in (1, 2):
        try:
            _post_incident_with_persons(thread_id, content, source_url, roster)
            return True
        except Exception as error:
            print(f"post attempt {attempt} failed for {label}: {error}")

    return False


def _post_incidents_and_complete_source_ids(
    postable_items: list[dict[str, Any]],
    roster: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    posted_items: list[dict[str, Any]] = []
    for postable_item in postable_items:
        # One unpostable item must not strand the rest of the batch at
        # "processing" -- that is what left 4060 rows stuck and re-processed.
        try:
            _post_incident_with_persons(
                postable_item["thread_id"],
                postable_item["content"],
                postable_item.get("source_url"),
                roster,
            )
            update_db(postable_item["source_id"], "completed")
        except Exception as error:
            print(f"post failed for {postable_item.get('source_id')}: {error}")
            continue

        posted_items.append(postable_item)

    return posted_items


def _post_main_output(
    main_output: list[dict[str, Any]],
    roster: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return _post_incidents_and_complete_source_ids(main_output, roster)


def _update_non_political_source_ids(non_political_source_ids: list[str]) -> None:
    for source_id in non_political_source_ids:
        update_db(source_id, "filtered")


def _post_secondary_thread_items(
    thread_items: list[dict[str, Any]],
    roster: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    # first candidate is the news item (real source_id); the rest are waiting-list incidents
    source_item, *waiting_list_incident_items = thread_items
    posted_items: list[dict[str, Any]] = []

    if _post_incident_with_retry(
        source_item["thread_id"],
        source_item["content"],
        source_item.get("source_url"),
        roster,
        label=source_item["source_id"],
    ):
        update_db(source_item["source_id"], "completed")
        posted_items.append(source_item)

    for incident_item in waiting_list_incident_items:
        # A promoted row carries only its stored content, so its people are
        # extracted here at promotion time rather than when it was queued.
        # One unpostable incident must not strand the thread the others were
        # confirmed against -- see _post_incidents_and_complete_source_ids.
        if not _post_incident_with_retry(
            incident_item["thread_id"],
            incident_item["content"],
            incident_item.get("source_url"),
            roster,
            label=incident_item.get("source_id", incident_item.get("waiting_list_id")),
        ):
            continue

        # Retire the waiting-list row so it cannot spawn this thread again, and
        # complete the article it came from.
        update_waitinglists(incident_item["waiting_list_id"], "completed")
        if incident_item.get("source_id"):
            update_db(incident_item["source_id"], "completed")
        posted_items.append(incident_item)

    return posted_items


def _post_secondary_output_item(
    waiting_list_item: dict[str, Any],
    roster: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Returns (posted_items, outcome), outcome is 'thread_created' or 'waiting_listed'."""
    if waiting_list_confidence_checker([waiting_list_item]):
        created_thread_items = _create_threads_from_waiting_list_item(waiting_list_item)
        posted_items = _post_secondary_thread_items(created_thread_items, roster)
        return posted_items, "thread_created"

    post_waitinglists(
        waiting_list_item["para_content"],
        waiting_list_item["vector"],
        waiting_list_item.get("source_url"),
        waiting_list_item.get("source_id"),
    )
    update_db(waiting_list_item["source_id"], "completed")
    return [], "waiting_listed"


def post_gold_level_data(gold_level_data: dict[str, Any]) -> dict[str, Any]:
    main_output = list(gold_level_data.get("main_output", []))
    secondary_output = list(gold_level_data.get("secondary_output", []))
    non_political_source_ids = list(gold_level_data.get("non_political_source_ids", []))

    _update_non_political_source_ids(non_political_source_ids)

    # Fetched once and threaded through both paths; it is the same for every
    # incident in the run.
    roster = fetch_person_roster()

    posted_main_output = _post_main_output(main_output, roster)

    final_secondary_output: list[dict[str, Any]] = []
    new_threads_created = 0
    waiting_listed_count = 0
    for waiting_list_item in secondary_output:
        try:
            posted_items, outcome = _post_secondary_output_item(waiting_list_item, roster)
        except Exception as error:
            print(f"waiting list post failed for {waiting_list_item.get('source_id')}: {error}")
            continue

        final_secondary_output.extend(posted_items)
        if outcome == "thread_created":
            new_threads_created += 1
        else:
            waiting_listed_count += 1

    return {
        "main_output": posted_main_output,
        "secondary_output": final_secondary_output,
        "combined": posted_main_output + final_secondary_output,
        "directly_appended_count": len(posted_main_output),
        "new_threads_created": new_threads_created,
        "waiting_listed_count": waiting_listed_count,
    }

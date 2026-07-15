import json
from typing import Any

from modules.fetch_api import fetch_api
from modules.llm_node import llm_node
from modules.prompt_loader import load_prompt


PERSONS_INVOLVED_PROMPT = "persons_involved_prompt.txt"
CACHE_URL = "https://poli-engine-backend.onrender.com/cache"


def _parse_json_response(response_text: str) -> Any:
    normalized_text = response_text.strip()
    if normalized_text.startswith("```"):
        normalized_text = normalized_text.removeprefix("```json").removeprefix("```").strip()
        if normalized_text.endswith("```"):
            normalized_text = normalized_text[:-3].strip()

    return json.loads(normalized_text)


def fetch_person_roster() -> list[dict[str, Any]]:
    """Fetch the {person_id, name} roster the model matches against.

    Call once per run, not per incident. The roster has to be in the prompt
    because incident text is Malayalam while persons.name is English, so no
    amount of string matching would connect the two.
    """
    cache = fetch_api(CACHE_URL)
    persons = cache.get("persons", []) if isinstance(cache, dict) else []
    return [
        {"person_id": person["person_id"], "name": person["name"]}
        for person in persons
        if person.get("person_id") is not None and person.get("name")
    ]


def _build_prompt(content: str, roster: list[dict[str, Any]]) -> str:
    prompt = load_prompt(PERSONS_INVOLVED_PROMPT)
    roster_json = json.dumps(roster, ensure_ascii=False)
    return f"{prompt}\nroster:\n{roster_json}\n\nincident:\n{content}"


def extract_persons(content: str, roster: list[dict[str, Any]]) -> list[int]:
    """Return the roster person_ids the incident is about.

    Fails closed: any parse problem yields []. An incident with no people
    attached is merely incomplete, whereas attaching the wrong person is a
    false statement about a real individual.
    """
    if not content or not roster:
        return []

    known_ids = {person["person_id"] for person in roster}

    try:
        payload = _parse_json_response(llm_node(prompt=_build_prompt(content, roster)))
    except Exception as error:
        print(f"person extraction failed, continuing with none: {error}")
        return []

    if isinstance(payload, dict):
        person_ids = payload.get("person_ids", [])
    elif isinstance(payload, list):
        person_ids = payload
    else:
        return []

    if not isinstance(person_ids, list):
        return []

    # Drop anything the model invented; only roster ids may reach the database.
    extracted_ids: list[int] = []
    for person_id in person_ids:
        if isinstance(person_id, bool):
            continue
        if isinstance(person_id, str) and person_id.strip().isdigit():
            person_id = int(person_id.strip())
        if isinstance(person_id, int) and person_id in known_ids and person_id not in extracted_ids:
            extracted_ids.append(person_id)

    return extracted_ids

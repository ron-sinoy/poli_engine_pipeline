import json
import time
from typing import Any

from google import genai

GEMINI_API_KEY = "AIzaSyBb8vXh2Sk_HH7nRPG_rwpPcfXWeZKU9Jk"
GEMINI_MODEL_NAME = "gemini-3.1-flash-lite"
MAX_LLM_ATTEMPTS = 7
RETRY_DELAY_SECONDS = 2


def generate_llm_response(prompt: str, model: str = GEMINI_MODEL_NAME) -> dict[str, Any]:
    """Run a Gemini prompt and retry transient failures up to the configured limit."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    last_error: Exception | None = None

    for attempt_number in range(1, MAX_LLM_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            raw_text = _extract_response_text(response).strip()
            if raw_text:
                parsed_json = _parse_json_payload(raw_text)
                return {
                    "raw_text": raw_text,
                    "parsed_json": parsed_json,
                }

            last_error = RuntimeError("Gemini returned an empty response.")
        except Exception as error:
            last_error = error

        if attempt_number < MAX_LLM_ATTEMPTS:
            time.sleep(RETRY_DELAY_SECONDS)

    if last_error is not None:
        raise RuntimeError(
            f"Gemini call failed after {MAX_LLM_ATTEMPTS} attempts."
        ) from last_error

    raise RuntimeError("Gemini call failed without returning a response.")


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text:
        return text

    candidates = getattr(response, "candidates", None)
    if not isinstance(candidates, list):
        return ""

    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        response_parts = getattr(content, "parts", None)
        if not isinstance(response_parts, list):
            continue

        for part in response_parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text:
                parts.append(part_text)

    return "\n".join(parts)


def _parse_json_payload(raw_text: str) -> Any:
    if not raw_text:
        return None

    for candidate in _json_candidates(raw_text):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    return None


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

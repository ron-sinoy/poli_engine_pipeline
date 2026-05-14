import json
import time
from typing import Any

from google import genai

from modules.progress_log import describe_payload, log_step

GEMINI_API_KEY = "AIzaSyBb8vXh2Sk_HH7nRPG_rwpPcfXWeZKU9Jk"
GEMINI_MODEL_NAME = "gemini-3.1-flash-lite"
MAX_LLM_ATTEMPTS = 7
RETRY_DELAY_SECONDS = 2


def generate_llm_response(prompt: str, model: str = GEMINI_MODEL_NAME) -> dict[str, Any]:
    """Run a Gemini prompt and retry transient failures up to the configured limit."""
    log_step(
        f"Preparing Gemini client for model={model} with prompt length {len(prompt)}."
    )
    client = genai.Client(api_key=GEMINI_API_KEY)
    last_error: Exception | None = None

    for attempt_number in range(1, MAX_LLM_ATTEMPTS + 1):
        log_step(
            f"Starting Gemini attempt {attempt_number} of {MAX_LLM_ATTEMPTS}."
        )
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            log_step(
                "Gemini returned a response object: "
                f"{describe_payload(response)}."
            )
            raw_text = _extract_response_text(response).strip()
            log_step(f"Extracted Gemini raw text with length {len(raw_text)}.")
            if raw_text:
                parsed_json = _parse_json_payload(raw_text)
                log_step(
                    "Gemini response handling complete with parsed payload "
                    f"{describe_payload(parsed_json)}."
                )
                return {
                    "raw_text": raw_text,
                    "parsed_json": parsed_json,
                }

            last_error = RuntimeError("Gemini returned an empty response.")
            log_step("Gemini returned empty text; scheduling retry if attempts remain.")
        except Exception as error:
            last_error = error
            log_step(f"Gemini attempt {attempt_number} raised error: {error!r}.")

        if attempt_number < MAX_LLM_ATTEMPTS:
            log_step(f"Sleeping {RETRY_DELAY_SECONDS} seconds before retry.")
            time.sleep(RETRY_DELAY_SECONDS)

    if last_error is not None:
        log_step(f"Gemini call exhausted retries with final error: {last_error!r}.")
        raise RuntimeError(
            f"Gemini call failed after {MAX_LLM_ATTEMPTS} attempts."
        ) from last_error

    log_step("Gemini call exhausted retries without a captured error.")
    raise RuntimeError("Gemini call failed without returning a response.")


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text:
        log_step("Using direct Gemini response.text value.")
        return text

    candidates = getattr(response, "candidates", None)
    if not isinstance(candidates, list):
        log_step("Gemini response had no candidate list.")
        return ""

    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        response_parts = getattr(content, "parts", None)
        if not isinstance(response_parts, list):
            log_step("Skipped a Gemini candidate without parts list.")
            continue

        for part in response_parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text:
                parts.append(part_text)
                log_step("Collected a text part from Gemini candidate.")

    return "\n".join(parts)


def _parse_json_payload(raw_text: str) -> Any:
    if not raw_text:
        log_step("Skipping JSON parsing because raw text was empty.")
        return None

    for candidate in _json_candidates(raw_text):
        try:
            parsed = json.loads(candidate)
            log_step(f"Successfully parsed JSON candidate as {describe_payload(parsed)}.")
            return parsed
        except json.JSONDecodeError:
            log_step("A Gemini JSON candidate failed to parse; trying next candidate.")
            continue

    log_step("No Gemini JSON candidate could be parsed.")
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

    log_step(f"Prepared {len(candidates)} JSON parse candidate(s) from Gemini text.")
    return candidates

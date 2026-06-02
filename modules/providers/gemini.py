from typing import Any

from google import genai

from modules.config import get_gemini_api_key, get_gemini_model
from modules.prompt_loader import load_prompt


def _build_client() -> genai.Client:
    return genai.Client(api_key=get_gemini_api_key())


def _extract_response_text(response: object) -> str:
    text = getattr(response, "text", "")
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", [])
    if not candidates:
        return ""

    content = getattr(candidates[0], "content", None)
    parts = getattr(content, "parts", [])
    text_parts: list[str] = []
    for part in parts:
        part_text = getattr(part, "text", "")
        if part_text:
            text_parts.append(part_text)

    return "".join(text_parts).strip()


def generate_gemini_response(
    prompt: str | None = None,
    model: str | None = None,
    *,
    prompt_name: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
) -> str:
    if prompt_name is not None:
        prompt = load_prompt(prompt_name)

    if prompt is None:
        raise ValueError("prompt or prompt_name is required")

    resolved_model = get_gemini_model(model)
    client = _build_client()

    request_config: dict[str, Any] = {}
    if temperature is not None:
        request_config["temperature"] = temperature
    if max_output_tokens is not None:
        request_config["max_output_tokens"] = max_output_tokens
    if top_p is not None:
        request_config["top_p"] = top_p
    if top_k is not None:
        request_config["top_k"] = top_k

    print(f"Gemini trying model: {resolved_model}")
    try:
        request_body: dict[str, Any] = {
            "model": resolved_model,
            "contents": prompt,
        }
        if request_config:
            request_body["config"] = request_config

        response = client.models.generate_content(**request_body)
        text = _extract_response_text(response)
        if text:
            print(f"Gemini model succeeded: {resolved_model}")
            return text

        print(f"Gemini model failed: {resolved_model} - empty content")
        raise ValueError(f"{resolved_model} returned empty content")
    except Exception as exc:
        print(f"Gemini model failed: {resolved_model} - {exc}")
        raise

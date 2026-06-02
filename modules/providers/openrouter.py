from openai import OpenAI

from modules.config import (
    get_openrouter_api_key,
    get_openrouter_base_url,
    get_openrouter_models,
)
from modules.prompt_loader import load_prompt


def _build_client() -> OpenAI:
    return OpenAI(
        base_url=get_openrouter_base_url(),
        api_key=get_openrouter_api_key(),
    )


def _extract_response_text(response: object) -> str:
    choices = getattr(response, "choices", [])
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", "")
    return (content or "").strip()


def generate_openrouter_response(
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

    client = _build_client()
    last_error: Exception | None = None

    for resolved_model in get_openrouter_models(model):
        print(f"OpenRouter trying model: {resolved_model}")
        try:
            request_body = {
                "model": resolved_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            }
            if temperature is not None:
                request_body["temperature"] = temperature
            if max_output_tokens is not None:
                request_body["max_tokens"] = max_output_tokens
            if top_p is not None:
                request_body["top_p"] = top_p

            response = client.chat.completions.create(**request_body)
            text = _extract_response_text(response)
            if text:
                print(f"OpenRouter model succeeded: {resolved_model}")
                return text

            print(f"OpenRouter model failed: {resolved_model} - empty content")
            last_error = ValueError(f"{resolved_model} returned empty content")
        except Exception as exc:
            print(f"OpenRouter model failed: {resolved_model} - {exc}")
            last_error = exc
            continue

    raise RuntimeError("OpenRouter response failed for all configured models") from last_error

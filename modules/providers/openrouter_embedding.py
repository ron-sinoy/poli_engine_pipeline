import json
from typing import Any

from openai import OpenAI

from modules.config import (
    get_openrouter_api_key,
    get_openrouter_base_url,
    get_openrouter_embedding_model,
)


def _build_client() -> OpenAI:
    return OpenAI(
        base_url=get_openrouter_base_url(),
        api_key=get_openrouter_api_key(),
    )


def _serialize_embedding_input(data: Any) -> str:
    if isinstance(data, str):
        return data

    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _extract_embedding(response: object) -> list[float]:
    data = getattr(response, "data", [])
    if not data:
        return []

    embedding = getattr(data[0], "embedding", [])
    return list(embedding or [])


def generate_openrouter_embedding(data: Any, model: str | None = None) -> list[float]:
    resolved_model = get_openrouter_embedding_model(model)
    input_text = _serialize_embedding_input(data)
    client = _build_client()

    print(f"OpenRouter trying embedding model: {resolved_model}")
    try:
        response = client.embeddings.create(
            model=resolved_model,
            input=input_text,
        )
        embedding = _extract_embedding(response)
        if embedding:
            print(f"OpenRouter embedding model succeeded: {resolved_model}")
            return embedding

        print(f"OpenRouter embedding model failed: {resolved_model} - empty embedding")
        raise ValueError(f"{resolved_model} returned empty embedding")
    except Exception as exc:
        print(f"OpenRouter embedding model failed: {resolved_model} - {exc}")
        raise

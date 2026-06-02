import json
from typing import Any

from google import genai

from modules.config import get_gemini_api_key, get_gemini_embedding_model


def _build_client() -> genai.Client:
    return genai.Client(api_key=get_gemini_api_key())


def _serialize_embedding_input(data: Any) -> str:
    if isinstance(data, str):
        return data

    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _extract_embedding(response: object) -> list[float]:
    embeddings = getattr(response, "embeddings", [])
    if embeddings:
        values = getattr(embeddings[0], "values", [])
        return list(values or [])

    embedding = getattr(response, "embedding", None)
    if embedding is not None:
        values = getattr(embedding, "values", embedding)
        return list(values or [])

    if isinstance(response, dict):
        if "embedding" in response:
            return list(response["embedding"] or [])
        if response.get("embeddings"):
            first_embedding = response["embeddings"][0]
            if isinstance(first_embedding, dict):
                return list(first_embedding.get("values", []) or [])

    return []


def generate_gemini_embedding(data: Any, model: str | None = None) -> list[float]:
    resolved_model = get_gemini_embedding_model(model)
    input_text = _serialize_embedding_input(data)
    client = _build_client()

    print(f"Gemini trying embedding model: {resolved_model}")
    try:
        response = client.models.embed_content(
            model=resolved_model,
            contents=input_text,
        )
        embedding = _extract_embedding(response)
        if embedding:
            print(f"Gemini embedding model succeeded: {resolved_model}")
            return embedding

        print(f"Gemini embedding model failed: {resolved_model} - empty embedding")
        raise ValueError(f"{resolved_model} returned empty embedding")
    except Exception as exc:
        print(f"Gemini embedding model failed: {resolved_model} - {exc}")
        raise

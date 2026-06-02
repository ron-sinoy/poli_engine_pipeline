import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OPENROUTER_MODELS = [
    "openai/gpt-oss-120b:free",                 # less known, free
    "meta-llama/llama-3.3-70b-instruct:free",  # popular but reliable
    "nvidia/nemotron-3-super-120b-a12b:free",  # less popular, large
    "qwen/qwen3-coder:free",                    # less traffic
    "deepseek/deepseek-v4-flash:free",          # last, most congested
]
DEFAULT_OPENROUTER_EMBEDDING_MODEL = "openai/text-embedding-3-small"
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
DEFAULT_GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"
OPENROUTER_BASE_URL_ENV = "OPENROUTER_BASE_URL"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL_ENV = "GEMINI_MODEL"
GEMINI_EMBEDDING_MODEL_ENV = "GEMINI_EMBEDDING_MODEL"

load_dotenv(PROJECT_ROOT / ".env")


def get_bronze_sources() -> list[dict[str, Any]]:
    # Parse bronze_sources.json and return as a list of {source, apis} dicts
    config_path = PROJECT_ROOT / "bronze_sources.json"
    parsed_sources = json.loads(config_path.read_text(encoding="utf-8"))
    expanded_sources = []
    for name, apis in parsed_sources.items():
        expanded_sources.append({
            "source": name,
            "apis": apis
        })
    return expanded_sources


def get_openrouter_api_key() -> str:
    api_key = os.getenv(OPENROUTER_API_KEY_ENV, "").strip()
    if not api_key:
        raise ValueError(f"{OPENROUTER_API_KEY_ENV} is required")

    return api_key


def get_openrouter_base_url() -> str:
    base_url = os.getenv(OPENROUTER_BASE_URL_ENV, "").strip()
    if base_url:
        return base_url.rstrip("/")

    return "https://openrouter.ai/api/v1"


def normalize_model_name(model: str) -> str:
    normalized_model = model.strip()
    if not normalized_model:
        raise ValueError("model is required")

    return normalized_model


def get_openrouter_models(model: str | None = None) -> list[str]:
    if model is not None:
        return [normalize_model_name(model)]

    return DEFAULT_OPENROUTER_MODELS.copy()


def get_openrouter_embedding_model(model: str | None = None) -> str:
    if model is not None:
        return normalize_model_name(model)

    return DEFAULT_OPENROUTER_EMBEDDING_MODEL


def get_gemini_api_key() -> str:
    api_key = os.getenv(GEMINI_API_KEY_ENV, "").strip()
    if not api_key:
        raise ValueError(f"{GEMINI_API_KEY_ENV} is required")

    return api_key


def get_gemini_model(model: str | None = None) -> str:
    if model is not None:
        return normalize_model_name(model)

    configured_model = os.getenv(GEMINI_MODEL_ENV, "").strip()
    if configured_model:
        return normalize_model_name(configured_model)

    return DEFAULT_GEMINI_MODEL


def get_gemini_embedding_model(model: str | None = None) -> str:
    if model is not None:
        return normalize_model_name(model)

    configured_model = os.getenv(GEMINI_EMBEDDING_MODEL_ENV, "").strip()
    if configured_model:
        return normalize_model_name(configured_model)

    return DEFAULT_GEMINI_EMBEDDING_MODEL

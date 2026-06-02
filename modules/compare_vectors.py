import json
import math
from pathlib import Path
from typing import Any


PARAMS_PATH = Path(__file__).resolve().parent.parent / "params.json"


def _load_params() -> dict[str, Any]:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))

def _normalize_vector(vector):
    print(type(vector))
    print(repr(vector)[:500])

    if isinstance(vector, str):
        import ast
        vector = ast.literal_eval(vector)

    return [float(value) for value in vector]


def _cosine_similarity(vector_a: Any, vector_b: Any) -> float:
    normalized_a = _normalize_vector(vector_a)
    normalized_b = _normalize_vector(vector_b)

    dot_product = sum(left * right for left, right in zip(normalized_a, normalized_b))
    magnitude_a = math.sqrt(sum(value * value for value in normalized_a))
    magnitude_b = math.sqrt(sum(value * value for value in normalized_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


import ast

def _normalize_thread_vectors(thread_vectors):
    if isinstance(thread_vectors, str):
        thread_vectors = ast.literal_eval(thread_vectors)

    if not thread_vectors:
        return []

    first_item = thread_vectors[0]

    if isinstance(first_item, (int, float)):
        return [_normalize_vector(thread_vectors)]

    return [_normalize_vector(vector) for vector in thread_vectors]


def _best_thread_score(vector_ref: Any, thread_vectors: Any) -> float:
    scores = [_cosine_similarity(vector_ref, thread_vector) for thread_vector in _normalize_thread_vectors(thread_vectors)]
    if not scores:
        return 0.0

    return max(scores)


def top_n_threads_classifier(
    vector_ref: Any,
    vectors_list: list[dict[str, Any]],
    count: int,
    *,
    confidence_level: float | None = None,
) -> list[dict[str, Any]]:
    params = _load_params() if confidence_level is None else None
    resolved_confidence = confidence_level if confidence_level is not None else float(params["confidence_level"])

    ranked_thread_ids: list[dict[str, Any]] = []
    for thread_item in vectors_list:
        thread_id = thread_item["thread_id"]
        thread_score = _best_thread_score(vector_ref, thread_item["thread_vectors"])
        if thread_score >= resolved_confidence:
            ranked_thread_ids.append(
                {
                    "thread_id": thread_id,
                    "title": thread_item["title"],
                    "scores": thread_score,
                    "summary": thread_item["summary"],
                }
            )

    ranked_thread_ids.sort(key=lambda item: item["scores"], reverse=True)
    return ranked_thread_ids[:count]


def build_compare_vectors_data(
    main_data: list[dict[str, Any]],
    vectors_list: list[dict[str, Any]],
    count: int | None = None,
) -> list[dict[str, Any]]:
    params = _load_params()
    resolved_count = count if count is not None else int(params["count_level_primary_threads"])
    confidence_level = float(params["confidence_level"])

    compared_data: list[dict[str, Any]] = []
    for item in main_data:
        compared_item = dict(item)
        compared_item["Threads"] = top_n_threads_classifier(
            item["vector"],
            vectors_list,
            resolved_count,
            confidence_level=confidence_level,
        )
        compared_data.append(compared_item)

    return compared_data

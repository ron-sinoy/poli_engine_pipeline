from typing import Any

from modules.check_db import check_db, get_seen_source_ids
from modules.filter_json import filter_json_keys, filter_json_values
from modules.insert_db import insert_db
from modules.source_id import relabel_source_id
from specific_modules.enrich_data import enrich_data
from specific_modules.url import complete_url


SILVER_KEYS = [
    "itemTitle",
    "itemTitleLead",
    "source_id",
    "source_url",
    "content",
    # "publishedTime",
    "relatedStoriesTopic",
]


def _relabel_candidates(bronze_level_data: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    candidates: list[tuple[str, dict[str, Any]]] = []
    for item in bronze_level_data:
        if not filter_json_values(item, "elementType", [0, 1]):
            continue

        if not filter_json_values(item, "sectionTitle", ["News"]):
            continue

        if not filter_json_values(item, "subSectionTitle", ["India", "Kerala"]):
            continue

        source_name = item["source"]
        candidates.append((source_name, relabel_source_id(source_name, item)))

    return candidates


def build_silver_level_data(bronze_level_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    silver_level_data: list[dict[str, Any]] = []

    # Relabel first so the whole batch can be checked against the backend in one
    # request instead of one per article.
    candidates = _relabel_candidates(bronze_level_data)
    seen_source_ids = get_seen_source_ids([item["source_id"] for _, item in candidates])

    for source_name, relabeled_item in candidates:
        if check_db(seen_source_ids, relabeled_item["source_id"]):
            continue

        relabeled_item["itemDetailURL"] = complete_url(source_name, relabeled_item["itemDetailURL"])
        relabeled_item["source_url"] = relabeled_item["itemDetailURL"]
        relabeled_item["content"] = enrich_data(source_name, relabeled_item["itemDetailURL"])
        insert_db(relabeled_item["source_id"])
        filtered_item = filter_json_keys(relabeled_item, SILVER_KEYS)
        silver_level_data.append(filtered_item)

    return silver_level_data

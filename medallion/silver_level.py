from typing import Any

from modules.check_db import check_db, get_source_ids
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


def build_silver_level_data(bronze_level_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    silver_level_data: list[dict[str, Any]] = []
    source_ids = get_source_ids()

    for item in bronze_level_data:
        if not filter_json_values(item, "elementType", [0, 1]):
            continue

        if not filter_json_values(item, "sectionTitle", ["News"]):
            continue

        if not filter_json_values(item, "subSectionTitle", ["India", "Kerala"]):
            continue

        source_name = item["source"]
        relabeled_item = relabel_source_id(source_name, item)
        if check_db(source_ids, relabeled_item["source_id"]):
            continue

        relabeled_item["itemDetailURL"] = complete_url(source_name, relabeled_item["itemDetailURL"])
        relabeled_item["source_url"] = relabeled_item["itemDetailURL"]
        relabeled_item["content"] = enrich_data(source_name, relabeled_item["itemDetailURL"])
        insert_db(relabeled_item["source_id"])
        filtered_item = filter_json_keys(relabeled_item, SILVER_KEYS)
        silver_level_data.append(filtered_item)

    return silver_level_data

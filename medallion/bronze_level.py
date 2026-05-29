from typing import Any

from modules.fetch_api import fetch_api
from modules.merge_data import merge_data
from specific_modules.filter_raw_data import filter_raw_data


def build_bronze_level_data(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fetch, filter, and merge bronze payloads into one list."""
    bronze_level_data: list[dict[str, Any]] = []

    for source_item in sources:
        source_name = source_item["source"]
        source_urls = source_item["apis"]

        for url in source_urls:
            #if source not defined, error raised inside filter
            cleaned_payload = filter_raw_data(source_name, fetch_api(url))

            for item in cleaned_payload:
                item["source"] = source_name

            bronze_level_data = merge_data(bronze_level_data, cleaned_payload)

    return bronze_level_data

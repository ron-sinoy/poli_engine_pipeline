from typing import Any

from modules.fetch_api import fetch_api
from modules.merge_data import merge_data
from specific_modules.filter_raw_data import filter_raw_data


def build_bronze_level_data(sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Fetch, filter, and merge bronze payloads source by source."""
    bronze_level_data: dict[str, Any] = {}

    for source_item in sources:
        source_name = source_item["source"]
        source_urls = source_item["apis"]

        for url in source_urls:
            #if source not defined, error raised inside filter
            cleaned_payload = filter_raw_data(source_name, fetch_api(url))

           #if its the first api of a source
            if source_name not in bronze_level_data:
                bronze_level_data[source_name] = cleaned_payload
                continue

            #second api onwards of saem source
            bronze_level_data[source_name] = merge_data(
                bronze_level_data[source_name], cleaned_payload
            )

    return bronze_level_data

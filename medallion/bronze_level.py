from typing import Any

from modules.fetch_api import fetch_api
from modules.merge_data import merge_data
from specific_modules.filter_raw_data import filter_raw_data


DEFAULT_URL_1 = "https://www.mathrubhumi.com/api/home-api-1"
DEFAULT_URL_2 = "https://www.mathrubhumi.com/api/home-api-2"


def build_bronze_level_data(
    url1: str = DEFAULT_URL_1, url2: str = DEFAULT_URL_2
) -> Any:
    """Fetch, clean, and merge the raw source payloads into bronze-level data."""
    data1 = _clean_source_payload(fetch_api(url1))
    data2 = _clean_source_payload(fetch_api(url2))
    return merge_data(data1, data2)


def _clean_source_payload(payload: Any) -> Any:
    return filter_raw_data(payload)

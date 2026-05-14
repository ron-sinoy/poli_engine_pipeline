from typing import Any

from modules.fetch_api import fetch_api
from modules.merge_data import merge_data
from modules.progress_log import describe_payload, log_step
from specific_modules.filter_raw_data import filter_raw_data


DEFAULT_URL_1 = "https://www.mathrubhumi.com/api/home-api-1"
DEFAULT_URL_2 = "https://www.mathrubhumi.com/api/home-api-2"


def build_bronze_level_data(
    url1: str = DEFAULT_URL_1, url2: str = DEFAULT_URL_2
) -> Any:
    """Fetch, clean, and merge the raw source payloads into bronze-level data."""
    log_step(f"Starting bronze stage with urls: {url1} and {url2}.")
    data1 = _clean_source_payload(fetch_api(url1))
    log_step(f"First bronze source cleaned into {describe_payload(data1)}.")
    data2 = _clean_source_payload(fetch_api(url2))
    log_step(f"Second bronze source cleaned into {describe_payload(data2)}.")
    log_step("Merging bronze source payloads.")
    return merge_data(data1, data2)


def _clean_source_payload(payload: Any) -> Any:
    log_step(f"Cleaning bronze source payload {describe_payload(payload)}.")
    return filter_raw_data(payload)

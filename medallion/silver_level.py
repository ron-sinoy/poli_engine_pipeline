from typing import Any

from modules.check_db import (
    filter_items_with_new_sourceids,
    get_sourceids,
    post_sourceids,
)
from modules.progress_log import describe_payload, log_step
from specific_modules.filter_bronze_level_data import filter_bronze_level_data
from specific_modules.enrich_silver_level_data import enrich_silver_level_data


def build_silver_level_data(bronze_level_data: Any) -> Any:
    """Filter bronze-level data into the silver-level dataset."""
    log_step(
        f"Starting silver stage with bronze payload {describe_payload(bronze_level_data)}."
    )
    silver_base_data = filter_bronze_level_data(bronze_level_data)
    log_step(f"Silver filter step produced {describe_payload(silver_base_data)}.")
    existing_sourceids = get_sourceids()
    silver_pending_data = filter_items_with_new_sourceids(
        silver_base_data, existing_sourceids
    )
    log_step(
        "Source id DB filter step produced "
        f"{describe_payload(silver_pending_data)}."
    )
    silver_level_data = enrich_silver_level_data(silver_pending_data)
    log_step(f"Silver enrichment step produced {describe_payload(silver_level_data)}.")
    post_sourceids(silver_level_data)
    log_step("Silver source id POST step completed.")
    return silver_level_data

from typing import Any

from modules.check_db import (
    filter_items_with_new_sourceids,
    get_sourceids,
    post_sourceids,
)
from specific_modules.filter_bronze_level_data import filter_bronze_level_data
from specific_modules.enrich_silver_level_data import enrich_silver_level_data


def build_silver_level_data(bronze_level_data: Any) -> Any:
    """Filter bronze-level data into the silver-level dataset."""
    silver_base_data = filter_bronze_level_data(bronze_level_data)
    existing_sourceids = get_sourceids()
    silver_pending_data = filter_items_with_new_sourceids(
        silver_base_data, existing_sourceids
    )
    silver_level_data = enrich_silver_level_data(silver_pending_data)
    post_sourceids(silver_level_data)
    return silver_level_data

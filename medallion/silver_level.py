from typing import Any

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
    return enrich_silver_level_data(silver_base_data)

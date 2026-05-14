from typing import Any

from modules.progress_log import describe_payload, log_step


def merge_data(data1: Any, data2: Any) -> Any:
    """Merge two JSON values into a new value.

    - dict + dict: merge top-level keys, where ``data2`` overrides duplicates.
    - list + list: concatenate both lists in order.
    """
    log_step(
        "Merging payloads "
        f"{describe_payload(data1)} and {describe_payload(data2)}."
    )
    if isinstance(data1, dict) and isinstance(data2, dict):
        merged = dict(data1)
        merged.update(data2)
        log_step(f"Dictionary merge complete: {describe_payload(merged)}.")
        return merged

    if isinstance(data1, list) and isinstance(data2, list):
        merged = [*data1, *data2]
        log_step(f"List merge complete: {describe_payload(merged)}.")
        return merged

    log_step("Merge failed because payload types were incompatible.")
    raise TypeError("merge_data expects both inputs to be dicts or both to be lists")

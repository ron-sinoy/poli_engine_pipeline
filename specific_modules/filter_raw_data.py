from typing import Any


def filter_raw_data(source: str, payload: Any) -> Any:
    if source == "mathrubhumi":
        return filter_mathrubhumi_raw_data(payload)

    raise ValueError(f"Unsupported bronze source: {source}")


def filter_mathrubhumi_raw_data(payload: Any) -> Any:
    """Return the nested ``home.data`` subtree from the raw API response."""
    if not isinstance(payload, dict):
        return None

    home = payload.get("home")
    if not isinstance(home, dict):
        return None

    return home.get("data")

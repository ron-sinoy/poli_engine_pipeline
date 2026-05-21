from typing import Any

def filter_raw_data(payload: dict[str, Any]) -> Any:
    """Return the nested ``home.data`` subtree from the raw API response."""
    if not isinstance(payload, dict):
        return None

    home = payload.get("home")
    if not isinstance(home, dict):
        return None

    return home.get("data")

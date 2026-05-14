from typing import Any

from modules.progress_log import describe_payload, log_step


def filter_raw_data(payload: dict[str, Any]) -> Any:
    """Return the nested ``home.data`` subtree from the raw API response."""
    if not isinstance(payload, dict):
        log_step("Raw payload was not a dict; returning None.")
        return None

    home = payload.get("home")
    if not isinstance(home, dict):
        log_step("Raw payload did not contain a valid home dict; returning None.")
        return None

    data = home.get("data")
    log_step(f"Extracted raw home.data payload as {describe_payload(data)}.")
    return data

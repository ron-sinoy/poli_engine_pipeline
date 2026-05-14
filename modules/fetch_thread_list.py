from typing import Any

from modules.fetch_api import fetch_api
from modules.progress_log import describe_payload, log_step


BACKEND_BASE_URL = "https://poli-engine-backend-production.up.railway.app"


def fetch_threads_list(base_url: str = BACKEND_BASE_URL) -> Any:
    """Fetch the current backend thread list."""
    url = f"{base_url.rstrip('/')}/threadsList"
    log_step(f"Fetching threads list from {url}.")
    payload = fetch_api(url)
    log_step(f"Finished fetching threads list: {describe_payload(payload)}.")
    return payload


def fetch_thread_by_id(thread_id: Any, base_url: str = BACKEND_BASE_URL) -> Any:
    """Fetch a single thread payload when a thread id is available."""
    if thread_id in (None, ""):
        log_step("Skipped thread fetch because thread_id was empty.")
        return None

    url = f"{base_url.rstrip('/')}/threads/{thread_id}"
    log_step(f"Fetching thread details for thread_id={thread_id} from {url}.")
    payload = fetch_api(url)
    log_step(
        "Finished fetching thread details for "
        f"thread_id={thread_id}: {describe_payload(payload)}."
    )
    return payload


def fetch_cache(base_url: str = BACKEND_BASE_URL) -> Any:
    """Fetch the backend cache payload used by the second gold pass."""
    url = f"{base_url.rstrip('/')}/cache"
    log_step(f"Fetching cache payload from {url}.")
    payload = fetch_api(url)
    log_step(f"Finished fetching cache payload: {describe_payload(payload)}.")
    return payload

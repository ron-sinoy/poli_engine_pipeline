from typing import Any

from modules.fetch_api import fetch_api


BACKEND_BASE_URL = "https://poli-engine-backend-production.up.railway.app"


def fetch_threads_list(base_url: str = BACKEND_BASE_URL) -> Any:
    """Fetch the current backend thread list."""
    url = f"{base_url.rstrip('/')}/threadsList"
    return fetch_api(url)


def fetch_thread_by_id(thread_id: Any, base_url: str = BACKEND_BASE_URL) -> Any:
    """Fetch a single thread payload when a thread id is available."""
    if thread_id in (None, ""):
        return None

    url = f"{base_url.rstrip('/')}/threads/{thread_id}"
    return fetch_api(url)


def fetch_cache(base_url: str = BACKEND_BASE_URL) -> Any:
    """Fetch the backend cache payload used by the second gold pass."""
    url = f"{base_url.rstrip('/')}/cache"
    return fetch_api(url)

from typing import Any
import httpx
from modules.progress_log import describe_payload, log_step

def fetch_api(url: str) -> Any:
    """Fetch JSON from a URL and return the parsed response body."""
    log_step(f"Starting HTTP fetch for {url}.")
    response = httpx.get(url, follow_redirects=True, timeout=None)
    log_step(f"Received HTTP response {response.status_code} for {url}.")
    response.raise_for_status()
    payload = response.json()
    log_step(f"Parsed JSON from {url} as {describe_payload(payload)}.")
    return payload

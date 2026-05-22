from typing import Any
import httpx

def fetch_api(url: str) -> Any:
    """Fetch JSON from a URL and return the parsed response body."""
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload

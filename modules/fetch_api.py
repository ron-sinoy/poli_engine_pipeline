from typing import Any
import httpx
import time

def fetch_api(url: str, retries: int = 3, retry_delay: int = 5) -> Any:
    """Fetch JSON from a URL and return the parsed response body."""
    for attempt in range(retries):
        try:
            response = httpx.get(url, follow_redirects=True, timeout=30)
            response.raise_for_status()
            return response.json()
        except (httpx.ConnectTimeout, httpx.HTTPStatusError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(retry_delay)
from typing import Any
import httpx
import time


def _raise_for_error_body(url: str, payload: Any) -> None:
    """A 200 carrying an error body must not be mistaken for data.

    The backend returns its Supabase failures as a JSON body. Without this the
    error dict flows on as if it were a result and silently degrades to an empty
    list, so a broken backend looks like "nothing matched".
    """
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(f"{url} returned an error body: {payload['error']} ({payload.get('details')})")


def fetch_api(url: str, retries: int = 3, retry_delay: int = 5) -> Any:
    """Fetch JSON from a URL and return the parsed response body."""
    for attempt in range(retries):
        try:
            response = httpx.get(url, follow_redirects=True, timeout=90)
            response.raise_for_status()
            payload = response.json()
            _raise_for_error_body(url, payload)
            return payload
        except (httpx.ConnectTimeout, httpx.HTTPStatusError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(retry_delay)


def post_api(url: str, json_body: Any, retries: int = 3, retry_delay: int = 5) -> Any:
    """POST JSON to a URL and return the parsed response body."""
    for attempt in range(retries):
        try:
            response = httpx.post(url, json=json_body, follow_redirects=True, timeout=90)
            response.raise_for_status()
            payload = response.json()
            _raise_for_error_body(url, payload)
            return payload
        except (httpx.ConnectTimeout, httpx.HTTPStatusError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(retry_delay)

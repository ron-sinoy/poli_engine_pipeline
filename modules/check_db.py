from typing import Any

from modules.fetch_api import post_api


SOURCE_IDS_EXISTS_URL = "https://poli-engine-backend.onrender.com/sourceids/exists"


def get_seen_source_ids(source_ids: list[str]) -> set[str]:
    """Return the subset of source_ids the pipeline has already claimed.

    Asks the backend about this batch only. Previously the whole table was
    downloaded and scanned in Python, which PostgREST capped at 1000 rows out of
    8264 -- so most articles looked new no matter what their status was.
    """
    if not source_ids:
        return set()

    rows = post_api(SOURCE_IDS_EXISTS_URL, {"source_ids": sorted(set(source_ids))})
    return {row["source_id"] for row in rows}


def check_db(seen_source_ids: set[str], source_id: str) -> bool:
    """An article is "seen" if a row exists at all.

    Statuses are not consulted. insert_db claims a source_id with status
    "processing", so treating only completed/filtered as seen made every
    unfinished article look brand new on the next run -- one id accumulated 61
    rows that way.
    """
    return source_id in seen_source_ids

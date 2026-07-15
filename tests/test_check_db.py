import unittest
from unittest.mock import patch

from modules.check_db import check_db, get_seen_source_ids


class TestCheckDb(unittest.TestCase):
    def test_get_seen_source_ids_asks_only_about_this_batch(self) -> None:
        rows = [
            {"source_id": "mt_#a", "status": "completed"},
            {"source_id": "mt_#b", "status": "processing"},
        ]

        with patch("modules.check_db.post_api", return_value=rows) as post_api:
            result = get_seen_source_ids(["mt_#b", "mt_#a", "mt_#b"])

        self.assertEqual(result, {"mt_#a", "mt_#b"})
        post_api.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/sourceids/exists",
            {"source_ids": ["mt_#a", "mt_#b"]},
        )

    def test_get_seen_source_ids_skips_the_request_for_an_empty_batch(self) -> None:
        with patch("modules.check_db.post_api") as post_api:
            result = get_seen_source_ids([])

        self.assertEqual(result, set())
        post_api.assert_not_called()

    def test_an_unfinished_article_counts_as_seen(self) -> None:
        # "processing" means a previous run already claimed this article. Treating
        # it as new is what re-scraped and re-embedded one article 61 times.
        with patch("modules.check_db.post_api", return_value=[{"source_id": "mt_#a", "status": "processing"}]):
            seen_source_ids = get_seen_source_ids(["mt_#a"])

        self.assertTrue(check_db(seen_source_ids, "mt_#a"))

    def test_an_unknown_article_is_not_seen(self) -> None:
        self.assertFalse(check_db({"mt_#a"}, "mt_#b"))


if __name__ == "__main__":
    unittest.main()

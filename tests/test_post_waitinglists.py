import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.post_waitinglists import post_waitinglists


class TestPostWaitingLists(unittest.TestCase):
    def test_post_waitinglists_posts_content_vectors_source_url_and_source_id(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True},
        )

        with patch("modules.post_waitinglists.httpx.post", return_value=response) as post:
            result = post_waitinglists(
                "Sample content",
                [0.1, 0.2],
                "https://example.com/news",
                "mt_#sample",
            )

        self.assertEqual(result, {"success": True})
        post.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/waitinglists",
            json={
                "content": "Sample content",
                "vectors": [0.1, 0.2],
                "source_url": "https://example.com/news",
                "source_id": "mt_#sample",
            },
            follow_redirects=True,
            timeout=30,
        )

    def test_rejects_a_row_that_could_never_be_promoted(self) -> None:
        with patch("modules.post_waitinglists.httpx.post") as post:
            with self.assertRaises(ValueError):
                post_waitinglists("Sample content", [0.1, 0.2], "", "mt_#sample")

            with self.assertRaises(ValueError):
                post_waitinglists("Sample content", [0.1, 0.2], "https://example.com/news", "")

        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.post_threads import post_threads


class TestPostThreads(unittest.TestCase):
    def test_post_threads_posts_title_and_summary(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True, "thread_id": 11},
        )

        with patch("modules.post_threads.httpx.post", return_value=response) as post:
            result = post_threads("മലയാളം തലക്കെട്ട്", "English summary")

        self.assertEqual(result, 11)
        post.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/threads",
            json={
                "title": "മലയാളം തലക്കെട്ട്",
                "summary": "English summary",
            },
            follow_redirects=True,
            timeout=30,
        )

    def test_post_threads_posts_vectors_when_given(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True, "thread_id": 12},
        )

        with patch("modules.post_threads.httpx.post", return_value=response) as post:
            result = post_threads("മലയാളം തലക്കെട്ട്", "English summary", [0.9, 0.8])

        self.assertEqual(result, 12)
        post.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/threads",
            json={
                "title": "മലയാളം തലക്കെട്ട്",
                "summary": "English summary",
                "vectors": [0.9, 0.8],
            },
            follow_redirects=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()

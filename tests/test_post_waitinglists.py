import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.post_waitinglists import post_waitinglists


class TestPostWaitingLists(unittest.TestCase):
    def test_post_waitinglists_posts_content_and_vectors(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True},
        )

        with patch("modules.post_waitinglists.httpx.post", return_value=response) as post:
            result = post_waitinglists("Sample content", [0.1, 0.2])

        self.assertEqual(result, {"success": True})
        post.assert_called_once_with(
            "https://poli-engine-backend-production.up.railway.app/waitinglists",
            json={
                "content": "Sample content",
                "vectors": [0.1, 0.2],
            },
            follow_redirects=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()

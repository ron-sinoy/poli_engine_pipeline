import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.post_incidents import post_incidents


class TestPostIncidents(unittest.TestCase):
    def test_post_incidents_posts_required_api_payload(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True},
        )

        with patch("modules.post_incidents.httpx.post", return_value=response) as post:
            result = post_incidents("985", "Paraphrased incident", "https://example.com/news")

        self.assertEqual(result, {"success": True})
        post.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/incidents",
            json={
                "thread_id": 985,
                "body": "Paraphrased incident",
                "source_url": "https://example.com/news",
                "persons_involved": [],
            },
            follow_redirects=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()

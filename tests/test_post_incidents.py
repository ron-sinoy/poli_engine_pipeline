import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.post_incidents import post_incidents


class TestPostIncidents(unittest.TestCase):
    def test_post_incidents_posts_thread_id_and_para_content(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True},
        )

        with patch("modules.post_incidents.httpx.post", return_value=response) as post:
            result = post_incidents("thread-a", "Paraphrased incident")

        self.assertEqual(result, {"success": True})
        post.assert_called_once_with(
            "https://poli-engine-backend-production.up.railway.app/incidents",
            json={
                "thread_id": "thread-a",
                "para_content": "Paraphrased incident",
            },
            follow_redirects=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()

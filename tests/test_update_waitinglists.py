import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.update_waitinglists import update_waitinglists


class TestUpdateWaitinglists(unittest.TestCase):
    def test_update_waitinglists_posts_completed_status(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"ok": True},
        )

        with patch("modules.update_waitinglists.httpx.post", return_value=response) as post:
            result = update_waitinglists(5, "completed")

        self.assertEqual(result, {"ok": True})
        post.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/waitinglists/update",
            json={
                "id": 5,
                "status": "completed",
            },
            follow_redirects=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()

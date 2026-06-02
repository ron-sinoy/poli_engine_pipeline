import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.update_db import update_db


class TestUpdateDb(unittest.TestCase):
    def test_update_db_posts_filtered_status(self) -> None:
        response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"ok": True},
        )

        with patch("modules.update_db.httpx.post", return_value=response) as post:
            result = update_db("mt_#sample", "filtered")

        self.assertEqual(result, {"ok": True})
        post.assert_called_once_with(
            "https://poli-engine-backend-production.up.railway.app/sourceids/update",
            json={
                "source_id": "mt_#sample",
                "status": "filtered",
            },
            follow_redirects=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()

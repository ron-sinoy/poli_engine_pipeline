import unittest
from unittest.mock import patch

from modules.content_waiting_list_incidents import content_waiting_list_incidents


class TestContentWaitingListIncidents(unittest.TestCase):
    def test_content_waiting_list_incidents_returns_id_and_content(self) -> None:
        waiting_list_incidents = [
            {"id": 1, "content": "Alpha"},
            {"id": 2, "content": "Beta"},
        ]

        with patch("modules.content_waiting_list_incidents.fetch_api", return_value=waiting_list_incidents):
            result = content_waiting_list_incidents()

        self.assertEqual(
            result,
            [
                {"id": 1, "content": "Alpha"},
                {"id": 2, "content": "Beta"},
            ],
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch

from modules.vector_waiting_list_incidents import vector_waiting_list_incidents


class TestVectorWaitingListIncidents(unittest.TestCase):
    def test_posts_the_query_vector_and_returns_the_ranked_rows(self) -> None:
        matched_rows = [
            {
                "id": 1,
                "content": "Alpha",
                "source_url": "https://example.com/1",
                "source_id": "mt_#a",
                "score": 0.93,
            },
            {
                "id": 2,
                "content": "Beta",
                "source_url": "https://example.com/2",
                "source_id": "mt_#b",
                "score": 0.87,
            },
        ]

        with patch("modules.vector_waiting_list_incidents.post_api", return_value=matched_rows) as post_api:
            with patch(
                "modules.vector_waiting_list_incidents._load_params",
                return_value={"count_level_waiting_list_incidents": 2},
            ):
                result = vector_waiting_list_incidents([1.0, 0.0])

        # Only the query vector goes out; the table is never downloaded.
        post_api.assert_called_once_with(
            "https://poli-engine-backend.onrender.com/waitinglists/match",
            {"vectors": [1.0, 0.0], "match_count": 2},
        )
        self.assertEqual(
            result,
            [
                {
                    "id": 1,
                    "content": "Alpha",
                    "source_url": "https://example.com/1",
                    "source_id": "mt_#a",
                    "confidence_score": 0.93,
                },
                {
                    "id": 2,
                    "content": "Beta",
                    "source_url": "https://example.com/2",
                    "source_id": "mt_#b",
                    "confidence_score": 0.87,
                },
            ],
        )

    def test_count_override_wins_over_params(self) -> None:
        with patch("modules.vector_waiting_list_incidents.post_api", return_value=[]) as post_api:
            with patch(
                "modules.vector_waiting_list_incidents._load_params",
                return_value={"count_level_waiting_list_incidents": 3},
            ):
                vector_waiting_list_incidents([1.0, 0.0], count=5)

        self.assertEqual(post_api.call_args[0][1]["match_count"], 5)


if __name__ == "__main__":
    unittest.main()

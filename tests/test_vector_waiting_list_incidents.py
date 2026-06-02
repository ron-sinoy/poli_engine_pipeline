import unittest
from unittest.mock import patch

from modules.vector_waiting_list_incidents import vector_waiting_list_incidents


class TestVectorWaitingListIncidents(unittest.TestCase):
    def test_vector_waiting_list_incidents_returns_top_ranked_rows(self) -> None:
        waiting_list_vectors = [
            {"id": 1, "vectors": [[1.0, 0.0], [0.0, 1.0]]},
            {"id": 2, "vectors": [[0.9, 0.1]]},
            {"id": 3, "vectors": [[-1.0, 0.0]]},
        ]

        with patch("modules.vector_waiting_list_incidents.fetch_api", return_value=waiting_list_vectors):
            with patch(
                "modules.vector_waiting_list_incidents._load_params",
                return_value={"count_level_waiting_list_incidents": 2},
            ):
                result = vector_waiting_list_incidents([1.0, 0.0])

        self.assertEqual(
            result,
            [
                {"id": 1, "vectors": [[1.0, 0.0], [0.0, 1.0]], "scores": 1.0},
                {"id": 2, "vectors": [[0.9, 0.1]], "scores": 0.9938837346736189},
            ],
        )


if __name__ == "__main__":
    unittest.main()

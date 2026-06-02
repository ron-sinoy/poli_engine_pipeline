import unittest
from unittest.mock import patch

from modules.compare_vectors import build_compare_vectors_data
from modules.compare_vectors import top_n_threads_classifier


class TestCompareVectors(unittest.TestCase):
    def test_compare_vectors_returns_top_matches_above_confidence(self) -> None:
        vectors_list = [
            {
                "thread_id": "thread-a",
                "title": "Thread A",
                "summary": "Summary A",
                "thread_vectors": [[1.0, 0.0], [0.0, 1.0]],
            },
            {
                "thread_id": "thread-b",
                "title": "Thread B",
                "summary": "Summary B",
                "thread_vectors": [[0.9, 0.1]],
            },
            {
                "thread_id": "thread-c",
                "title": "Thread C",
                "summary": "Summary C",
                "thread_vectors": [[-1.0, 0.0]],
            },
        ]

        with patch("modules.compare_vectors._load_params", return_value={"confidence_level": 0.5, "count_level_primary_threads": 2}):
            thread_ids = top_n_threads_classifier([1.0, 0.0], vectors_list, 2)

        self.assertEqual(
            thread_ids,
            [
                {"thread_id": "thread-a", "title": "Thread A", "scores": 1.0, "summary": "Summary A"},
                {"thread_id": "thread-b", "title": "Thread B", "scores": 0.9938837346736189, "summary": "Summary B"},
            ],
        )

    def test_build_compare_vectors_data_keeps_source_id_and_vector_only(self) -> None:
        main_data = [
            {"source_id": "mt_#1", "vector": [1.0, 0.0]},
            {"source_id": "mt_#2", "vector": [0.0, 1.0]},
        ]
        vectors_list = [
            {
                "thread_id": "thread-a",
                "title": "Thread A",
                "summary": "Summary A",
                "thread_vectors": [[1.0, 0.0]],
            },
            {
                "thread_id": "thread-b",
                "title": "Thread B",
                "summary": "Summary B",
                "thread_vectors": [[0.0, 1.0]],
            },
        ]

        with patch("modules.compare_vectors._load_params", return_value={"confidence_level": 0.5, "count_level_primary_threads": 1}):
            compared_data = build_compare_vectors_data(main_data, vectors_list)

        self.assertEqual(
            compared_data,
            [
                {
                    "source_id": "mt_#1",
                    "vector": [1.0, 0.0],
                    "Threads": [{"thread_id": "thread-a", "title": "Thread A", "scores": 1.0, "summary": "Summary A"}],
                },
                {
                    "source_id": "mt_#2",
                    "vector": [0.0, 1.0],
                    "Threads": [{"thread_id": "thread-b", "title": "Thread B", "scores": 1.0, "summary": "Summary B"}],
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()

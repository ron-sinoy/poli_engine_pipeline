import unittest
from pathlib import Path
from unittest.mock import patch

from modules.confidence_checker import confidence_checker


class TestConfidenceChecker(unittest.TestCase):
    def test_confidence_checker_uses_benchmark_from_params(self) -> None:
        with patch("modules.confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch(
                "pathlib.Path.read_text",
                return_value='{"confidence_level": 0.8, "count_level_primary_threads": 3}',
            ):
                self.assertTrue(
                    confidence_checker(
                        [
                            {"confidence_level": 0.9, "thread_id": "thread-a"},
                            {"confidence_level": 0.8, "thread_id": "thread-b"},
                        ]
                    )
                )

    def test_confidence_checker_fails_below_benchmark(self) -> None:
        with patch("modules.confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch(
                "pathlib.Path.read_text",
                return_value='{"confidence_level": 0.8, "count_level_primary_threads": 3}',
            ):
                self.assertFalse(
                    confidence_checker(
                        [
                            {"confidence_level": 0.9, "thread_id": "thread-a"},
                            {"confidence_level": 0.79, "thread_id": "thread-b"},
                        ]
                    )
                )

    def test_confidence_checker_fails_when_thread_id_is_null(self) -> None:
        with patch("modules.confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch(
                "pathlib.Path.read_text",
                return_value='{"confidence_level": 0.8, "count_level_primary_threads": 3}',
            ):
                self.assertFalse(
                    confidence_checker(
                        [
                            {"confidence_level": 0.9, "thread_id": None},
                        ]
                    )
                )


if __name__ == "__main__":
    unittest.main()

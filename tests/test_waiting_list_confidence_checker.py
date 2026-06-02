import unittest
from pathlib import Path
from unittest.mock import patch

from modules.waiting_list_confidence_checker import waiting_list_confidence_checker


class TestWaitingListConfidenceChecker(unittest.TestCase):
    def test_waiting_list_confidence_checker_passes_when_both_top_scores_clear_benchmark(self) -> None:
        with patch("modules.waiting_list_confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch(
                "pathlib.Path.read_text",
                return_value='{"confidence_level": 0.8, "count_level_primary_threads": 3, "count_level_waiting_list_incidents": 3}',
            ):
                self.assertTrue(
                    waiting_list_confidence_checker(
                        [
                            {
                                "incidentList": [
                                    {"confidence_score": 0.9},
                                    {"confidence_score": 0.8},
                                ]
                            }
                        ]
                    )
                )

    def test_waiting_list_confidence_checker_fails_when_one_score_is_below_benchmark(self) -> None:
        with patch("modules.waiting_list_confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch(
                "pathlib.Path.read_text",
                return_value='{"confidence_level": 0.8, "count_level_primary_threads": 3, "count_level_waiting_list_incidents": 3}',
            ):
                self.assertFalse(
                    waiting_list_confidence_checker(
                        [
                            {
                                "incidentList": [
                                    {"confidence_score": 0.9},
                                    {"confidence_score": 0.79},
                                ]
                            }
                        ]
                    )
                )


if __name__ == "__main__":
    unittest.main()

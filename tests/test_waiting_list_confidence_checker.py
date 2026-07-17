import unittest
from pathlib import Path
from unittest.mock import patch

from modules.waiting_list_confidence_checker import waiting_list_confidence_checker


PARAMS_JSON = (
    '{"confidence_level": 0.8, "count_level_primary_threads": 3, '
    '"count_level_waiting_list_incidents": 3, "required_waiting_list_matches": 1}'
)


class TestWaitingListConfidenceChecker(unittest.TestCase):
    def test_waiting_list_confidence_checker_passes_when_top_score_clears_benchmark(self) -> None:
        with patch("modules.waiting_list_confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch("pathlib.Path.read_text", return_value=PARAMS_JSON):
                self.assertTrue(
                    waiting_list_confidence_checker(
                        [
                            {
                                "incidentList": [
                                    {"confidence_score": 0.9},
                                ]
                            }
                        ]
                    )
                )

    def test_waiting_list_confidence_checker_fails_when_top_score_is_below_benchmark(self) -> None:
        with patch("modules.waiting_list_confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch("pathlib.Path.read_text", return_value=PARAMS_JSON):
                self.assertFalse(
                    waiting_list_confidence_checker(
                        [
                            {
                                "incidentList": [
                                    {"confidence_score": 0.79},
                                ]
                            }
                        ]
                    )
                )

    def test_waiting_list_confidence_checker_fails_when_no_incidents_are_matched(self) -> None:
        with patch("modules.waiting_list_confidence_checker.PARAMS_PATH", Path("/tmp/params.json")):
            with patch("pathlib.Path.read_text", return_value=PARAMS_JSON):
                self.assertFalse(waiting_list_confidence_checker([{"incidentList": []}]))


if __name__ == "__main__":
    unittest.main()

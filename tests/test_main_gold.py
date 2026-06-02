import unittest
from pathlib import Path
from unittest.mock import patch

import main


class TestMainGold(unittest.TestCase):
    def test_main_writes_gold_results_file(self) -> None:
        bronze_data = [{"bronze": 1}]
        silver_data = [{"silver": 2}]
        gold_data = [
            {
                "source_id": "mt_#sample",
                "thread_id": "thread-a",
                "content": "Paraphrased incident",
            }
        ]
        gold_wrapper = {
            "main_output": gold_data,
            "secondary_output": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-b",
                    "content": "Waiting list incident",
                }
            ],
            "combined": gold_data
            + [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-b",
                    "content": "Waiting list incident",
                }
            ],
        }

        with patch("main.get_bronze_sources", return_value=[{"source": "mathrubhumi", "apis": []}]):
            with patch("main.build_bronze_level_data", return_value=bronze_data):
                with patch("main.build_silver_level_data", return_value=silver_data):
                    with patch("main.build_gold_level_data", return_value=gold_wrapper):
                        with patch("main.write_json_file") as write_json_file:
                            result = main.main()

        self.assertEqual(result, (bronze_data, silver_data, gold_wrapper))
        write_json_file.assert_any_call(Path("results/results_bronze_level.json"), bronze_data)
        write_json_file.assert_any_call(Path("results/results_silver_level.json"), silver_data)
        write_json_file.assert_any_call(Path("results/main_output_gold.json"), gold_wrapper["main_output"])
        write_json_file.assert_any_call(
            Path("results/secondary_output_gold.json"),
            gold_wrapper["secondary_output"],
        )
        write_json_file.assert_any_call(Path("results/results_gold_level.json"), gold_wrapper["combined"])


if __name__ == "__main__":
    unittest.main()

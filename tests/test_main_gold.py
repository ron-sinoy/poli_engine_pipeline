import unittest
from pathlib import Path
from unittest.mock import patch

import main


class TestMainGold(unittest.TestCase):
    def test_main_writes_post_processed_gold_results_file(self) -> None:
        bronze_data = [{"bronze": 1}]
        silver_data = [{"silver": 2}]
        gold_data = {
            "main_output": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "content": "Paraphrased incident",
                }
            ],
            "secondary_output": [
                {
                    "para_content": "Waiting list incident",
                    "source_id": "mt_#sample",
                    "vector": [0.1, 0.2],
                    "incidentList": [
                        {
                            "id": 5,
                            "content": "Waiting list content 5",
                            "confidence_score": 0.93,
                        }
                    ],
                }
            ],
            "combined": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "content": "Paraphrased incident",
                }
            ],
            "non_political_source_ids": ["mt_#other"],
        }
        gold_wrapper = {
            "main_output": gold_data["main_output"],
            "secondary_output": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-b",
                    "content": "Waiting list incident",
                }
            ],
            "combined": gold_data["main_output"]
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
                    with patch("main.build_gold_level_data", return_value=gold_data):
                        with patch("main.post_gold_level_data", return_value=gold_wrapper) as post_gold_level_data:
                            with patch("main.write_json_file") as write_json_file:
                                result = main.main()

        self.assertEqual(result, (bronze_data, silver_data, gold_wrapper))
        post_gold_level_data.assert_called_once_with(gold_data)
        write_json_file.assert_any_call(Path("results/results_bronze_level.json"), bronze_data)
        write_json_file.assert_any_call(Path("results/results_silver_level.json"), silver_data)
        write_json_file.assert_any_call(Path("results/pre_post_gold_level.json"), gold_data)
        write_json_file.assert_any_call(Path("results/main_output_gold.json"), gold_wrapper["main_output"])
        write_json_file.assert_any_call(
            Path("results/secondary_output_gold.json"),
            gold_wrapper["secondary_output"],
        )
        write_json_file.assert_any_call(Path("results/results_gold_level.json"), gold_wrapper["combined"])


if __name__ == "__main__":
    unittest.main()

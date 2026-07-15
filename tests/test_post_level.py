import json
import unittest
from unittest.mock import call, patch

from medallion.post_level import post_gold_level_data


class TestPostLevel(unittest.TestCase):
    def test_post_gold_level_data_posts_main_output_and_creates_secondary_thread(self) -> None:
        gold_level_data = {
            "main_output": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "content": "Paraphrased incident",
                    "source_url": "https://example.com/main",
                }
            ],
            "secondary_output": [
                {
                    "para_content": "Waiting list incident",
                    "source_id": "mt_#sample-secondary",
                    "vector": [0.1, 0.2],
                    "source_url": "https://example.com/secondary",
                    "incidentList": [
                        {
                            "id": 5,
                            "source_id": "mt_#waiting-5",
                            "content": "Waiting list content 5",
                            "source_url": "https://example.com/waiting-5",
                            "confidence_score": 0.93,
                        },
                        {
                            "id": 6,
                            "source_id": "mt_#waiting-6",
                            "content": "Waiting list content 6",
                            "source_url": "https://example.com/waiting-6",
                            "confidence_score": 0.81,
                        },
                    ],
                }
            ],
            "non_political_source_ids": ["mt_#other"],
        }
        expected_secondary_output = [
            {
                "source_id": "mt_#sample-secondary",
                "thread_id": 11,
                "content": "Waiting list incident",
                "source_url": "https://example.com/secondary",
            },
            {
                "waiting_list_id": 5,
                "source_id": "mt_#waiting-5",
                "thread_id": 11,
                "content": "Waiting list content 5",
                "source_url": "https://example.com/waiting-5",
            },
            {
                "waiting_list_id": 6,
                "source_id": "mt_#waiting-6",
                "thread_id": 11,
                "content": "Waiting list content 6",
                "source_url": "https://example.com/waiting-6",
            },
        ]
        expected_output = {
            "main_output": gold_level_data["main_output"],
            "secondary_output": expected_secondary_output,
            "combined": gold_level_data["main_output"] + expected_secondary_output,
        }

        with patch("medallion.post_level.waiting_list_confidence_checker", return_value=True) as waiting_list_confidence_checker:
            with patch("medallion.post_level.load_prompt", return_value="Waiting list thread prompt") as load_prompt:
                with patch(
                    "medallion.post_level.llm_node",
                    return_value=json.dumps({"title": "മലയാളം തലക്കെട്ട്", "summary": "English summary"}, ensure_ascii=False),
                ) as llm_node:
                    with patch("medallion.post_level.generate_gemini_embedding", return_value=[0.9, 0.8]) as generate_gemini_embedding:
                        with patch("medallion.post_level.post_threads", return_value=11) as post_threads:
                            with patch("medallion.post_level.post_incidents") as post_incidents:
                                with patch("medallion.post_level.update_db") as update_db:
                                    with patch("medallion.post_level.update_waitinglists") as update_waitinglists:
                                        with patch("medallion.post_level.post_waitinglists") as post_waitinglists:
                                            result = post_gold_level_data(gold_level_data)

        self.assertEqual(result, expected_output)
        waiting_list_confidence_checker.assert_called_once_with([gold_level_data["secondary_output"][0]])
        load_prompt.assert_called_once_with("waiting_list_thread_prompt.txt")
        llm_node.assert_called_once()
        self.assertIn("Waiting list thread prompt", llm_node.call_args.kwargs["prompt"])
        generate_gemini_embedding.assert_called_once_with(
            {
                "title": "മലയാളം തലക്കെട്ട്",
                "summary": "English summary",
            }
        )
        post_threads.assert_called_once_with("മലയാളം തലക്കെട്ട്", "English summary", [0.9, 0.8])
        # The thread is born holding all three incidents that justified it.
        post_incidents.assert_has_calls(
            [
                call("thread-a", "Paraphrased incident", "https://example.com/main"),
                call(11, "Waiting list incident", "https://example.com/secondary"),
                call(11, "Waiting list content 5", "https://example.com/waiting-5"),
                call(11, "Waiting list content 6", "https://example.com/waiting-6"),
            ]
        )
        self.assertEqual(post_incidents.call_count, 4)
        update_db.assert_has_calls(
            [
                call("mt_#other", "filtered"),
                call("mt_#sample", "completed"),
                call("mt_#sample-secondary", "completed"),
                call("mt_#waiting-5", "completed"),
                call("mt_#waiting-6", "completed"),
            ]
        )
        self.assertEqual(update_db.call_count, 5)
        # Consumed rows are retired by their waiting-list id so they cannot
        # spawn the same thread again on the next run.
        update_waitinglists.assert_has_calls(
            [
                call(5, "completed"),
                call(6, "completed"),
            ]
        )
        self.assertEqual(update_waitinglists.call_count, 2)
        post_waitinglists.assert_not_called()

    def test_post_gold_level_data_posts_low_confidence_waiting_list_items(self) -> None:
        gold_level_data = {
            "main_output": [],
            "secondary_output": [
                {
                    "para_content": "Waiting list incident",
                    "source_id": "mt_#sample-secondary",
                    "vector": [0.1, 0.2],
                    "source_url": "https://example.com/secondary",
                    "incidentList": [
                        {
                            "id": 5,
                            "content": "Waiting list content 5",
                            "confidence_score": 0.50,
                        },
                        {
                            "id": 6,
                            "content": "Waiting list content 6",
                            "confidence_score": 0.40,
                        },
                    ],
                }
            ],
            "non_political_source_ids": [],
        }

        with patch("medallion.post_level.waiting_list_confidence_checker", return_value=False) as waiting_list_confidence_checker:
            with patch("medallion.post_level.post_threads") as post_threads:
                with patch("medallion.post_level.post_incidents") as post_incidents:
                    with patch("medallion.post_level.update_db") as update_db:
                        with patch("medallion.post_level.post_waitinglists") as post_waitinglists:
                            result = post_gold_level_data(gold_level_data)

        self.assertEqual(
            result,
            {
                "main_output": [],
                "secondary_output": [],
                "combined": [],
            },
        )
        waiting_list_confidence_checker.assert_called_once_with([gold_level_data["secondary_output"][0]])
        post_threads.assert_not_called()
        post_incidents.assert_not_called()
        # The row carries its source_id so it can complete its article when promoted.
        post_waitinglists.assert_called_once_with(
            "Waiting list incident",
            [0.1, 0.2],
            "https://example.com/secondary",
            "mt_#sample-secondary",
        )
        update_db.assert_called_once_with("mt_#sample-secondary", "completed")

    def test_one_failing_item_does_not_strand_the_rest_of_the_batch(self) -> None:
        gold_level_data = {
            "main_output": [
                {
                    "source_id": "mt_#bad",
                    "thread_id": "thread-a",
                    "content": "Doomed incident",
                    "source_url": "https://example.com/bad",
                },
                {
                    "source_id": "mt_#good",
                    "thread_id": "thread-b",
                    "content": "Fine incident",
                    "source_url": "https://example.com/good",
                },
            ],
            "secondary_output": [],
            "non_political_source_ids": [],
        }

        with patch(
            "medallion.post_level.post_incidents",
            side_effect=[RuntimeError("HTTP 500"), None],
        ) as post_incidents:
            with patch("medallion.post_level.update_db") as update_db:
                result = post_gold_level_data(gold_level_data)

        # The good item still lands, and only it is reported as posted.
        self.assertEqual(result["main_output"], [gold_level_data["main_output"][1]])
        self.assertEqual(post_incidents.call_count, 2)
        update_db.assert_called_once_with("mt_#good", "completed")

    def test_secondary_thread_posts_every_waiting_list_incident(self) -> None:
        gold_level_data = {
            "main_output": [],
            "secondary_output": [{
                "para_content": "Current incident",
                "source_id": "mt_#current",
                "source_url": "https://example.com/current",
                "vector": [0.1, 0.2],
                "incidentList": [{
                    "id": 5,
                    "source_id": "mt_#waiting-5",
                    "content": "Waiting incident",
                    "source_url": "https://example.com/waiting-5",
                    "confidence_score": 0.9,
                }],
            }],
            "non_political_source_ids": [],
        }

        with patch("medallion.post_level.waiting_list_confidence_checker", return_value=True):
            with patch("medallion.post_level._create_threads_from_waiting_list_item", return_value=[
                {"source_id": "mt_#current", "thread_id": 11, "content": "Current incident", "source_url": "https://example.com/current"},
                {"waiting_list_id": 5, "source_id": "mt_#waiting-5", "thread_id": 11, "content": "Waiting incident", "source_url": "https://example.com/waiting-5"},
            ]):
                with patch("medallion.post_level.post_incidents") as post_incidents:
                    with patch("medallion.post_level.update_db") as update_db:
                        with patch("medallion.post_level.update_waitinglists") as update_waitinglists:
                            result = post_gold_level_data(gold_level_data)

        self.assertEqual(len(result["secondary_output"]), 2)
        post_incidents.assert_has_calls([
            call(11, "Current incident", "https://example.com/current"),
            call(11, "Waiting incident", "https://example.com/waiting-5"),
        ])
        self.assertEqual(post_incidents.call_count, 2)
        update_waitinglists.assert_called_once_with(5, "completed")
        update_db.assert_has_calls([
            call("mt_#current", "completed"),
            call("mt_#waiting-5", "completed"),
        ])


if __name__ == "__main__":
    unittest.main()

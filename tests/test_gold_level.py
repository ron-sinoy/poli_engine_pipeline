import json
import unittest
from pathlib import Path
from unittest.mock import call, patch

from medallion.gold_level import build_gold_level_data


class TestGoldLevel(unittest.TestCase):
    def test_translates_text_fields_embeds_and_keeps_political_output_when_thread_id_exists(self) -> None:
        silver_level_data = [
            {
                "itemTitle": "മലയാളം ശീർഷകം",
                "itemTitleLead": "മലയാളം ലീഡ്",
                "source_id": "mt_#sample",
                "relatedStoriesTopic": "Topic",
                "content": "മലയാളം ഉള്ളടക്കം",
            }
        ]
        translated_item = {
            "itemTitle": "English title",
            "itemTitleLead": "English lead",
            "source_id": "mt_#sample",
            "relatedStoriesTopic": "Topic",
            "content": "English content",
        }
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "confidence_level": 0.42,
                }
            ],
            "non-political": ["mt_#other"],
        }
        expected_political_output = [
            {
                "source_id": "mt_#sample",
                "thread_id": "thread-a",
                "content": "Paraphrased incident",
            }
        ]
        expected_gold_output = {
            "main_output": expected_political_output,
            "secondary_output": [],
            "combined": expected_political_output,
        }
        threads_internal = [
            {
                "thread_id": "thread-a",
                "title": "Thread A",
                "summary": "Summary A",
                "thread_vectors": [[0.1, 0.2]],
            },
            {
                "thread_id": "thread-b",
                "title": "Thread B",
                "summary": "Summary B",
                "thread_vectors": [[-0.1, -0.2]],
            },
        ]

        with patch(
            "medallion.gold_level.load_prompt",
            side_effect=["Translate prompt", "Classifier prompt"],
        ) as load_prompt:
            with patch(
                "medallion.gold_level.llm_node",
                side_effect=[
                    json.dumps(translated_item, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                ],
            ) as llm_node:
                with patch("medallion.gold_level.generate_gemini_embedding", return_value=[0.1, 0.2]) as generate_gemini_embedding:
                    with patch("medallion.gold_level.fetch_api", return_value=threads_internal) as fetch_api:
                        with patch("medallion.gold_level.update_db") as update_db:
                            with patch("medallion.gold_level.confidence_checker", return_value=False) as confidence_checker:
                                with patch("medallion.gold_level.content_waiting_list_incidents") as content_waiting_list_incidents:
                                    with patch("medallion.gold_level.vector_waiting_list_incidents") as vector_waiting_list_incidents:
                                        gold_level_data = build_gold_level_data(silver_level_data)

        self.assertEqual(gold_level_data, expected_gold_output)
        self.assertEqual(llm_node.call_count, 2)
        translation_prompt = llm_node.call_args_list[0].kwargs["prompt"]
        classifier_prompt = llm_node.call_args_list[1].kwargs["prompt"]
        self.assertIn("Translate prompt", translation_prompt)
        self.assertIn('"itemTitle": "മലയാളം ശീർഷകം"', translation_prompt)
        self.assertIn("Classifier prompt", classifier_prompt)
        self.assertIn('"thread_id": "thread-a"', classifier_prompt)
        generate_gemini_embedding.assert_called_once_with(
            {
                "itemTitle": "English title",
                "itemTitleLead": "English lead",
                "relatedStoriesTopic": "Topic",
                "content": "English content",
            }
        )
        load_prompt.assert_any_call("prompt_translate.txt")
        load_prompt.assert_any_call("isPolitical_classifier_prompt.txt")
        fetch_api.assert_called_once()
        update_db.assert_called_once_with("mt_#other", "filtered")
        confidence_checker.assert_called_once_with(
            [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "confidence_level": 0.42,
                    "vector": [0.1, 0.2],
                }
            ]
        )
        content_waiting_list_incidents.assert_not_called()
        vector_waiting_list_incidents.assert_not_called()

    def test_else_branch_creates_threads_for_null_thread_items(self) -> None:
        silver_level_data = [
            {
                "itemTitle": "ശീർഷകം",
                "itemTitleLead": "ലീഡ്",
                "source_id": "mt_#1",
                "relatedStoriesTopic": "Topic",
                "content": "ഉള്ളടക്കം",
            }
        ]

        translated_item = {
            "itemTitle": "Title",
            "itemTitleLead": "Lead",
            "source_id": "mt_#1",
            "relatedStoriesTopic": "Topic",
            "content": "Content",
        }
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#1",
                    "thread_id": None,
                    "confidence_level": 0.42,
                }
            ],
            "non-political": [],
        }
        waiting_list_content = [
            {"id": 5, "content": "Waiting list content 5"},
            {"id": 6, "content": "Waiting list content 6"},
            {"id": 7, "content": "Waiting list content 7"},
        ]
        waiting_list_classification_output = [
            {
                "para_content": "Paraphrased incident",
                "source_id": "mt_#1",
                "vector": [0.1, 0.2],
                "incidentList": [
                    {"id": 5, "content": "Waiting list content 5", "confidence_score": 0.93},
                    {"id": 6, "content": "Waiting list content 6", "confidence_score": 0.81},
                    {"id": 7, "content": "Waiting list content 7", "confidence_score": 0.5},
                ],
            }
        ]
        thread_metadata = {"title": "മലയാളം തലക്കെട്ട്", "summary": "English summary"}

        with patch(
            "medallion.gold_level.load_prompt",
            side_effect=[
                "Translate prompt",
                "Classifier prompt",
                "Waiting list classification prompt",
                "Waiting list thread prompt",
            ],
        ) as load_prompt:
            with patch(
                "medallion.gold_level.llm_node",
                side_effect=[
                    json.dumps(translated_item, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps(waiting_list_classification_output, ensure_ascii=False),
                    json.dumps(thread_metadata, ensure_ascii=False),
                ],
            ) as llm_node:
                with patch(
                    "medallion.gold_level.generate_gemini_embedding",
                    side_effect=[[0.1, 0.2], [0.9, 0.8]],
                ) as generate_gemini_embedding:
                    with patch(
                        "medallion.gold_level.fetch_api",
                        return_value=[
                            {
                                "thread_id": "thread-a",
                                "title": "Thread A",
                                "summary": "Summary A",
                                "thread_vectors": [[0.1, 0.2]],
                            }
                        ],
                    ) as fetch_api:
                        with patch("medallion.gold_level.update_db") as update_db:
                            with patch("medallion.gold_level.confidence_checker", return_value=False) as confidence_checker:
                                with patch(
                                    "medallion.gold_level.content_waiting_list_incidents",
                                    return_value=waiting_list_content,
                                ) as content_waiting_list_incidents:
                                    with patch(
                                        "medallion.gold_level.vector_waiting_list_incidents",
                                        return_value=[
                                            {"id": 5, "vectors": [[0.9, 0.1]], "scores": 0.98},
                                            {"id": 6, "vectors": [[0.8, 0.2]], "scores": 0.92},
                                            {"id": 7, "vectors": [[0.7, 0.3]], "scores": 0.5},
                                        ],
                                    ) as vector_waiting_list_incidents:
                                        with patch(
                                            "medallion.gold_level.waiting_list_confidence_checker",
                                            return_value=True,
                                        ) as waiting_list_confidence_checker:
                                            with patch("medallion.gold_level.post_waitinglists") as post_waitinglists:
                                                with patch(
                                                    "medallion.gold_level.post_threads",
                                                    return_value=11,
                                                ) as post_threads:
                                                    gold_level_data = build_gold_level_data(silver_level_data)

        expected_secondary_output = [
            {
                "source_id": "mt_#1",
                "content": "Paraphrased incident",
                "thread_id": 11,
            },
            {
                "source_id": 5,
                "content": "Waiting list content 5",
                "thread_id": 11,
            },
            {
                "source_id": 6,
                "content": "Waiting list content 6",
                "thread_id": 11,
            },
        ]
        self.assertEqual(
            gold_level_data,
            {
                "main_output": [],
                "secondary_output": expected_secondary_output,
                "combined": expected_secondary_output,
            },
        )
        update_db.assert_not_called()
        confidence_checker.assert_called_once_with(
            [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#1",
                    "thread_id": None,
                    "confidence_level": 0.42,
                    "vector": [0.1, 0.2],
                }
            ]
        )
        load_prompt.assert_any_call("waiting_list_classification_prompt.txt")
        load_prompt.assert_any_call("waiting_list_thread_prompt.txt")
        self.assertEqual(llm_node.call_count, 4)
        waiting_list_prompt = llm_node.call_args_list[2].kwargs["prompt"]
        thread_prompt = llm_node.call_args_list[3].kwargs["prompt"]
        self.assertIn("Waiting list classification prompt", waiting_list_prompt)
        self.assertIn('"para_content": "Paraphrased incident"', waiting_list_prompt)
        self.assertIn("Waiting list thread prompt", thread_prompt)
        self.assertIn('"source_id": "mt_#1"', thread_prompt)
        self.assertIn('"source_id": 5', thread_prompt)
        self.assertIn('"source_id": 6', thread_prompt)
        generate_gemini_embedding.assert_has_calls(
            [
                call(
                    {
                        "itemTitle": "Title",
                        "itemTitleLead": "Lead",
                        "relatedStoriesTopic": "Topic",
                        "content": "Content",
                    }
                ),
                call(
                    {
                        "title": "മലയാളം തലക്കെട്ട്",
                        "summary": "English summary",
                    }
                ),
            ]
        )
        fetch_api.assert_called_once()
        content_waiting_list_incidents.assert_called_once()
        vector_waiting_list_incidents.assert_called_once_with([0.1, 0.2])
        waiting_list_confidence_checker.assert_called_once_with(
            [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#1",
                    "vector": [0.1, 0.2],
                    "incidentList": [
                        {"id": 5, "content": "Waiting list content 5", "confidence_score": 0.93},
                        {"id": 6, "content": "Waiting list content 6", "confidence_score": 0.81},
                    ],
                }
            ]
        )
        post_waitinglists.assert_not_called()
        post_threads.assert_called_once_with("മലയാളം തലക്കെട്ട്", "English summary")

    def test_null_thread_id_forces_waiting_list_route(self) -> None:
        silver_level_data = [
            {
                "itemTitle": "ശീർഷകം",
                "itemTitleLead": "ലീഡ്",
                "source_id": "mt_#null",
                "relatedStoriesTopic": "Topic",
                "content": "ഉള്ളടക്കം",
            }
        ]

        translated_item = {
            "itemTitle": "Title",
            "itemTitleLead": "Lead",
            "source_id": "mt_#null",
            "relatedStoriesTopic": "Topic",
            "content": "Content",
        }
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#null",
                    "thread_id": None,
                    "confidence_level": 0.42,
                }
            ],
            "non-political": [],
        }
        waiting_list_content = [
            {"id": 8, "content": "Waiting list content 8"},
            {"id": 9, "content": "Waiting list content 9"},
        ]
        waiting_list_classification_output = [
            {
                "para_content": "Paraphrased incident",
                "source_id": "mt_#null",
                "vector": [0.4, 0.5],
                "incidentList": [
                    {"id": 8, "content": "Waiting list content 8", "confidence_score": 0.96},
                    {"id": 9, "content": "Waiting list content 9", "confidence_score": 0.91},
                ],
            }
        ]

        with patch(
            "medallion.gold_level.load_prompt",
            side_effect=["Translate prompt", "Classifier prompt", "Waiting list classification prompt"],
        ) as load_prompt:
            with patch(
                "medallion.gold_level.llm_node",
                side_effect=[
                    json.dumps(translated_item, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps(waiting_list_classification_output, ensure_ascii=False),
                ],
            ) as llm_node:
                with patch("medallion.gold_level.generate_gemini_embedding", return_value=[0.4, 0.5]):
                    with patch(
                        "medallion.gold_level.fetch_api",
                        return_value=[
                            {
                                "thread_id": "thread-a",
                                "title": "Thread A",
                                "summary": "Summary A",
                                "thread_vectors": [[0.1, 0.2]],
                            }
                        ],
                    ):
                        with patch("medallion.gold_level.update_db") as update_db:
                            with patch(
                                "modules.confidence_checker.PARAMS_PATH",
                                Path("/tmp/params.json"),
                            ):
                                with patch(
                                    "pathlib.Path.read_text",
                                    return_value='{"confidence_level": 0.8, "count_level_primary_threads": 3, "count_level_waiting_list_incidents": 3}',
                                ):
                                    with patch(
                                        "medallion.gold_level.content_waiting_list_incidents",
                                        return_value=waiting_list_content,
                                    ) as content_waiting_list_incidents:
                                        with patch(
                                            "medallion.gold_level.vector_waiting_list_incidents",
                                            return_value=[
                                                {"id": 8, "vectors": [[0.4, 0.5]], "scores": 0.97},
                                                {"id": 9, "vectors": [[0.3, 0.4]], "scores": 0.9},
                                            ],
                                        ) as vector_waiting_list_incidents:
                                            with patch(
                                                "medallion.gold_level.waiting_list_confidence_checker",
                                                return_value=False,
                                            ) as waiting_list_confidence_checker:
                                                with patch("medallion.gold_level.post_waitinglists") as post_waitinglists:
                                                    with patch("medallion.gold_level.post_threads") as post_threads:
                                                        gold_level_data = build_gold_level_data(silver_level_data)

        self.assertEqual(
            gold_level_data,
            {
                "main_output": [],
                "secondary_output": [],
                "combined": [],
            },
        )
        self.assertEqual(llm_node.call_count, 3)
        self.assertIn("Waiting list classification prompt", llm_node.call_args_list[2].kwargs["prompt"])
        update_db.assert_not_called()
        content_waiting_list_incidents.assert_called_once()
        vector_waiting_list_incidents.assert_called_once_with([0.4, 0.5])
        waiting_list_confidence_checker.assert_called_once_with(
            [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#null",
                    "vector": [0.4, 0.5],
                    "incidentList": [
                        {"id": 8, "content": "Waiting list content 8", "confidence_score": 0.96},
                        {"id": 9, "content": "Waiting list content 9", "confidence_score": 0.91},
                    ],
                }
            ]
        )
        post_waitinglists.assert_called_once_with("Paraphrased incident", [0.4, 0.5])
        post_threads.assert_not_called()
        load_prompt.assert_any_call("isPolitical_classifier_prompt.txt")
        load_prompt.assert_any_call("waiting_list_classification_prompt.txt")

    def test_waiting_list_classification_prompt_is_slimmed_and_rehydrates_content(self) -> None:
        long_para_content = "Paraphrased incident " + ("A" * 5000)
        long_waiting_list_content_8 = "Waiting list content 8 " + ("B" * 5000)
        long_waiting_list_content_9 = "Waiting list content 9 " + ("C" * 5000)

        silver_level_data = [
            {
                "itemTitle": "ശീർഷകം",
                "itemTitleLead": "ലീഡ്",
                "source_id": "mt_#slim",
                "relatedStoriesTopic": "Topic",
                "content": "ഉള്ളടക്കം",
            }
        ]

        translated_item = {
            "itemTitle": "Title",
            "itemTitleLead": "Lead",
            "source_id": "mt_#slim",
            "relatedStoriesTopic": "Topic",
            "content": "Content",
        }
        classifier_output = {
            "political": [
                {
                    "para_content": long_para_content,
                    "source_id": "mt_#slim",
                    "thread_id": None,
                    "confidence_level": 0.42,
                }
            ],
            "non-political": [],
        }
        waiting_list_content = [
            {"id": 8, "content": long_waiting_list_content_8},
            {"id": 9, "content": long_waiting_list_content_9},
        ]
        waiting_list_classification_output = [
            {
                "para_content": long_para_content[:240],
                "source_id": "mt_#slim",
                "incidentList": [
                    {"id": 8, "content": "Truncated waiting list content 8", "confidence_score": 0.96},
                    {"id": 9, "content": "Truncated waiting list content 9", "confidence_score": 0.91},
                ],
            }
        ]

        with patch(
            "medallion.gold_level.load_prompt",
            side_effect=["Translate prompt", "Classifier prompt", "Waiting list classification prompt"],
        ) as load_prompt:
            with patch(
                "medallion.gold_level.llm_node",
                side_effect=[
                    json.dumps(translated_item, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps(waiting_list_classification_output, ensure_ascii=False),
                ],
            ) as llm_node:
                with patch("medallion.gold_level.generate_gemini_embedding", return_value=[0.4, 0.5]):
                    with patch(
                        "medallion.gold_level.fetch_api",
                        return_value=[
                            {
                                "thread_id": "thread-a",
                                "title": "Thread A",
                                "summary": "Summary A",
                                "thread_vectors": [[0.1, 0.2]],
                            }
                        ],
                    ):
                        with patch("medallion.gold_level.update_db") as update_db:
                            with patch("medallion.gold_level.confidence_checker", return_value=False):
                                with patch(
                                    "medallion.gold_level.content_waiting_list_incidents",
                                    return_value=waiting_list_content,
                                ):
                                    with patch(
                                        "medallion.gold_level.vector_waiting_list_incidents",
                                        return_value=[
                                            {"id": 8, "vectors": [[0.4, 0.5]], "scores": 0.97},
                                            {"id": 9, "vectors": [[0.3, 0.4]], "scores": 0.9},
                                        ],
                                    ):
                                        with patch(
                                            "medallion.gold_level.waiting_list_confidence_checker",
                                            return_value=False,
                                        ) as waiting_list_confidence_checker:
                                            with patch("medallion.gold_level.post_waitinglists") as post_waitinglists:
                                                with patch("medallion.gold_level.post_threads") as post_threads:
                                                    gold_level_data = build_gold_level_data(silver_level_data)

        self.assertEqual(
            gold_level_data,
            {
                "main_output": [],
                "secondary_output": [],
                "combined": [],
            },
        )
        self.assertEqual(llm_node.call_count, 3)
        waiting_list_prompt = llm_node.call_args_list[2].kwargs["prompt"]
        self.assertIn("Waiting list classification prompt", waiting_list_prompt)
        self.assertIn("...[truncated]", waiting_list_prompt)
        self.assertNotIn(long_para_content, waiting_list_prompt)
        self.assertNotIn(long_waiting_list_content_8, waiting_list_prompt)
        self.assertNotIn(long_waiting_list_content_9, waiting_list_prompt)
        self.assertNotIn('"vector"', waiting_list_prompt)
        waiting_list_confidence_checker.assert_called_once_with(
            [
                {
                    "para_content": long_para_content,
                    "source_id": "mt_#slim",
                    "vector": [0.4, 0.5],
                    "incidentList": [
                        {"id": 8, "content": long_waiting_list_content_8, "confidence_score": 0.96},
                        {"id": 9, "content": long_waiting_list_content_9, "confidence_score": 0.91},
                    ],
                }
            ]
        )
        post_waitinglists.assert_called_once_with(long_para_content, [0.4, 0.5])
        post_threads.assert_not_called()
        update_db.assert_not_called()


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from unittest.mock import patch

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
        expected_gold_output = {
            "main_output": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "content": "Paraphrased incident",
                }
            ],
            "secondary_output": [],
            "combined": [
                {
                    "source_id": "mt_#sample",
                    "thread_id": "thread-a",
                    "content": "Paraphrased incident",
                }
            ],
            "non_political_source_ids": ["mt_#other"],
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
                        with patch("medallion.gold_level.confidence_checker", return_value=False) as confidence_checker:
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

    def test_waiting_list_branch_returns_classified_waiting_list_items(self) -> None:
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

        with patch(
            "medallion.gold_level.load_prompt",
            side_effect=[
                "Translate prompt",
                "Classifier prompt",
                "Waiting list classification prompt",
            ],
        ) as load_prompt:
            with patch(
                "medallion.gold_level.llm_node",
                side_effect=[
                    json.dumps(translated_item, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps(waiting_list_classification_output, ensure_ascii=False),
                ],
            ) as llm_node:
                with patch(
                    "medallion.gold_level.generate_gemini_embedding",
                    return_value=[0.1, 0.2],
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
                        with patch("medallion.gold_level.confidence_checker", return_value=False):
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
                                    gold_level_data = build_gold_level_data(silver_level_data)

        self.assertEqual(
            gold_level_data,
            {
                "main_output": [],
                "secondary_output": [
                    {
                        "para_content": "Paraphrased incident",
                        "source_id": "mt_#1",
                        "vector": [0.1, 0.2],
                        "incidentList": [
                            {"id": 5, "content": "Waiting list content 5", "confidence_score": 0.93},
                            {"id": 6, "content": "Waiting list content 6", "confidence_score": 0.81},
                        ],
                    }
                ],
                "combined": [
                    {
                        "para_content": "Paraphrased incident",
                        "source_id": "mt_#1",
                        "vector": [0.1, 0.2],
                        "incidentList": [
                            {"id": 5, "content": "Waiting list content 5", "confidence_score": 0.93},
                            {"id": 6, "content": "Waiting list content 6", "confidence_score": 0.81},
                        ],
                    }
                ],
                "non_political_source_ids": [],
            },
        )
        self.assertEqual(llm_node.call_count, 3)
        waiting_list_prompt = llm_node.call_args_list[2].kwargs["prompt"]
        self.assertIn("Waiting list classification prompt", waiting_list_prompt)
        self.assertIn('"para_content": "Paraphrased incident"', waiting_list_prompt)
        generate_gemini_embedding.assert_called_once_with(
            {
                "itemTitle": "Title",
                "itemTitleLead": "Lead",
                "relatedStoriesTopic": "Topic",
                "content": "Content",
            }
        )
        load_prompt.assert_any_call("prompt_translate.txt")
        load_prompt.assert_any_call("isPolitical_classifier_prompt.txt")
        load_prompt.assert_any_call("waiting_list_classification_prompt.txt")
        fetch_api.assert_called_once()
        content_waiting_list_incidents.assert_called_once()
        vector_waiting_list_incidents.assert_called_once_with([0.1, 0.2])

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
                    ) as fetch_api:
                        with patch("medallion.gold_level.confidence_checker", return_value=False):
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
                                    gold_level_data = build_gold_level_data(silver_level_data)

        self.assertEqual(
            gold_level_data,
            {
                "main_output": [],
                "secondary_output": [
                    {
                        "para_content": "Paraphrased incident",
                        "source_id": "mt_#null",
                        "vector": [0.4, 0.5],
                        "incidentList": [
                            {"id": 8, "content": "Waiting list content 8", "confidence_score": 0.96},
                            {"id": 9, "content": "Waiting list content 9", "confidence_score": 0.91},
                        ],
                    }
                ],
                "combined": [
                    {
                        "para_content": "Paraphrased incident",
                        "source_id": "mt_#null",
                        "vector": [0.4, 0.5],
                        "incidentList": [
                            {"id": 8, "content": "Waiting list content 8", "confidence_score": 0.96},
                            {"id": 9, "content": "Waiting list content 9", "confidence_score": 0.91},
                        ],
                    }
                ],
                "non_political_source_ids": [],
            },
        )
        self.assertEqual(llm_node.call_count, 3)
        self.assertIn("Waiting list classification prompt", llm_node.call_args_list[2].kwargs["prompt"])
        fetch_api.assert_called_once()
        content_waiting_list_incidents.assert_called_once()
        vector_waiting_list_incidents.assert_called_once_with([0.4, 0.5])
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
                    ) as fetch_api:
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
                                    gold_level_data = build_gold_level_data(silver_level_data)

        self.assertEqual(
            gold_level_data,
            {
                "main_output": [],
                "secondary_output": [
                    {
                        "para_content": long_para_content,
                        "source_id": "mt_#slim",
                        "vector": [0.4, 0.5],
                        "incidentList": [
                            {"id": 8, "content": long_waiting_list_content_8, "confidence_score": 0.96},
                            {"id": 9, "content": long_waiting_list_content_9, "confidence_score": 0.91},
                        ],
                    }
                ],
                "combined": [
                    {
                        "para_content": long_para_content,
                        "source_id": "mt_#slim",
                        "vector": [0.4, 0.5],
                        "incidentList": [
                            {"id": 8, "content": long_waiting_list_content_8, "confidence_score": 0.96},
                            {"id": 9, "content": long_waiting_list_content_9, "confidence_score": 0.91},
                        ],
                    }
                ],
                "non_political_source_ids": [],
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
        load_prompt.assert_any_call("waiting_list_classification_prompt.txt")
        fetch_api.assert_called_once()


if __name__ == "__main__":
    unittest.main()

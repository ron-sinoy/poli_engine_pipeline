import json
import unittest
from unittest.mock import patch

from medallion.gold_level import build_gold_level_data


SILVER_ITEM = {
    "itemTitle": "മലയാളം ശീർഷകം",
    "itemTitleLead": "മലയാളം ലീഡ്",
    "source_id": "mt_#sample",
    "relatedStoriesTopic": "Topic",
    "content": "മലയാളം ഉള്ളടക്കം",
    "source_url": "https://example.com/sample",
}

TRANSLATED_ITEM = {
    "itemTitle": "English title",
    "itemTitleLead": "English lead",
    "source_id": "mt_#sample",
    "relatedStoriesTopic": "Topic",
    "content": "English content",
}

THREAD_MATCHES = [
    {"thread_id": 986, "title": "Thread A", "summary": "Summary A", "scores": 0.91},
    {"thread_id": 987, "title": "Thread B", "summary": "Summary B", "scores": 0.83},
]


class TestGoldLevel(unittest.TestCase):
    def _run(self, llm_responses, *, thread_matches=THREAD_MATCHES, waiting_list=None, prompts=None):
        """Drive build_gold_level_data with every network boundary stubbed."""
        prompts = prompts or ["Translate prompt", "Classifier prompt", "Waiting list prompt"]
        with patch("medallion.gold_level.load_prompt", side_effect=prompts):
            with patch("medallion.gold_level.llm_node", side_effect=llm_responses) as llm_node:
                with patch("medallion.gold_level.generate_gemini_embedding", return_value=[0.1, 0.2]):
                    with patch("medallion.gold_level.match_threads", return_value=thread_matches) as match_threads:
                        with patch(
                            "medallion.gold_level.vector_waiting_list_incidents",
                            return_value=waiting_list or [],
                        ) as vector_waiting_list_incidents:
                            result = build_gold_level_data([SILVER_ITEM])

        return result, llm_node, match_threads, vector_waiting_list_incidents

    def test_direct_path_uses_the_cosine_score_not_the_models_number(self) -> None:
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "thread_id": 986,
                    # A model that ignores instructions and invents a score must
                    # not be able to influence the decision.
                    "confidence_level": 0.42,
                }
            ],
            "non-political": ["mt_#other"],
        }

        with patch("medallion.gold_level.confidence_checker", return_value=True) as confidence_checker:
            result, _, match_threads, _ = self._run(
                [
                    json.dumps(TRANSLATED_ITEM, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                ]
            )

        self.assertEqual(
            result["main_output"],
            [
                {
                    "source_id": "mt_#sample",
                    "thread_id": 986,
                    "content": "Paraphrased incident",
                    "source_url": "https://example.com/sample",
                }
            ],
        )
        self.assertEqual(result["non_political_source_ids"], ["mt_#other"])
        match_threads.assert_called_once_with([0.1, 0.2])
        # 0.91 is thread 986's real cosine score; 0.42 was the model's invention.
        checked_item = confidence_checker.call_args[0][0][0]
        self.assertEqual(checked_item["confidence_level"], 0.91)
        self.assertEqual(checked_item["thread_id"], 986)

    def test_a_thread_id_the_model_invented_is_rejected(self) -> None:
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "thread_id": 999,  # not in the Threads list
                }
            ],
            "non-political": [],
        }

        with patch("medallion.gold_level.confidence_checker", return_value=False) as confidence_checker:
            self._run(
                [
                    json.dumps(TRANSLATED_ITEM, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                ]
            )

        # No score exists for an invented thread, so it cannot take the direct path.
        checked_item = confidence_checker.call_args[0][0][0]
        self.assertIsNone(checked_item["thread_id"])
        self.assertIsNone(checked_item["confidence_level"])

    def test_a_numeric_string_thread_id_still_matches_its_score(self) -> None:
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "thread_id": "987",
                }
            ],
            "non-political": [],
        }

        with patch("medallion.gold_level.confidence_checker", return_value=True) as confidence_checker:
            self._run(
                [
                    json.dumps(TRANSLATED_ITEM, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                ]
            )

        checked_item = confidence_checker.call_args[0][0][0]
        self.assertEqual(checked_item["thread_id"], 987)
        self.assertEqual(checked_item["confidence_level"], 0.83)

    def test_no_thread_match_routes_the_item_to_the_waiting_list(self) -> None:
        classifier_output = {
            "political": [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "thread_id": None,
                }
            ],
            "non-political": [],
        }
        waiting_list = [
            {
                "id": 5,
                "content": "Waiting list content 5",
                "source_url": "https://example.com/5",
                "source_id": "mt_#w5",
                "confidence_score": 0.93,
            },
            {
                "id": 6,
                "content": "Waiting list content 6",
                "source_url": "https://example.com/6",
                "source_id": "mt_#w6",
                "confidence_score": 0.81,
            },
        ]
        waiting_list_classification = [
            {
                "para_content": "Paraphrased incident",
                "source_id": "mt_#sample",
                "incidentList": [
                    {"id": 5, "is_related": True},
                    {"id": 6, "is_related": True},
                ],
            }
        ]

        with patch("medallion.gold_level.confidence_checker", return_value=False):
            result, _, _, vector_waiting_list_incidents = self._run(
                [
                    json.dumps(TRANSLATED_ITEM, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps(waiting_list_classification, ensure_ascii=False),
                ],
                waiting_list=waiting_list,
            )

        self.assertEqual(result["main_output"], [])
        vector_waiting_list_incidents.assert_called_once_with([0.1, 0.2])
        self.assertEqual(
            result["secondary_output"],
            [
                {
                    "para_content": "Paraphrased incident",
                    "source_id": "mt_#sample",
                    "vector": [0.1, 0.2],
                    "source_url": "https://example.com/sample",
                    "incidentList": [
                        {
                            "id": 5,
                            "content": "Waiting list content 5",
                            "confidence_score": 0.93,
                            "source_url": "https://example.com/5",
                            "source_id": "mt_#w5",
                        },
                    ],
                }
            ],
        )

    def test_incidents_the_model_calls_unrelated_are_dropped(self) -> None:
        classifier_output = {
            "political": [
                {"para_content": "Paraphrased incident", "source_id": "mt_#sample", "thread_id": None}
            ],
            "non-political": [],
        }
        waiting_list = [
            {
                "id": 5,
                "content": "Related",
                "source_url": "https://example.com/5",
                "source_id": "mt_#w5",
                "confidence_score": 0.93,
            },
            {
                "id": 6,
                "content": "Same topic, different story",
                "source_url": "https://example.com/6",
                "source_id": "mt_#w6",
                "confidence_score": 0.92,
            },
        ]
        waiting_list_classification = [
            {
                "para_content": "Paraphrased incident",
                "source_id": "mt_#sample",
                "incidentList": [
                    {"id": 5, "is_related": True},
                    {"id": 6, "is_related": False},
                ],
            }
        ]

        with patch("medallion.gold_level.confidence_checker", return_value=False):
            result, _, _, _ = self._run(
                [
                    json.dumps(TRANSLATED_ITEM, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps(waiting_list_classification, ensure_ascii=False),
                ],
                waiting_list=waiting_list,
            )

        # A high cosine score is not enough on its own; both must agree.
        incident_list = result["secondary_output"][0]["incidentList"]
        self.assertEqual([incident["id"] for incident in incident_list], [5])

    def test_waiting_list_prompt_is_slimmed_and_withholds_the_score(self) -> None:
        classifier_output = {
            "political": [
                {"para_content": "Paraphrased incident", "source_id": "mt_#sample", "thread_id": None}
            ],
            "non-political": [],
        }
        waiting_list = [
            {
                "id": 5,
                "content": "W" * 400,
                "source_url": "https://example.com/5",
                "source_id": "mt_#w5",
                "confidence_score": 0.93,
            },
        ]

        with patch("medallion.gold_level.confidence_checker", return_value=False):
            _, llm_node, _, _ = self._run(
                [
                    json.dumps(TRANSLATED_ITEM, ensure_ascii=False),
                    json.dumps(classifier_output, ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                ],
                waiting_list=waiting_list,
            )

        waiting_list_prompt = llm_node.call_args_list[2].kwargs["prompt"]
        self.assertIn("Waiting list prompt", waiting_list_prompt)
        self.assertIn("...[truncated]", waiting_list_prompt)
        # The model must not see the score it is forbidden to estimate.
        self.assertNotIn("confidence_score", waiting_list_prompt)
        self.assertNotIn("0.93", waiting_list_prompt)


if __name__ == "__main__":
    unittest.main()

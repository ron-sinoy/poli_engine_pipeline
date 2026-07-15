import json
import unittest
from unittest.mock import patch

from modules.extract_persons import extract_persons, fetch_person_roster


ROSTER = [
    {"person_id": 1, "name": "Pinarayi Vijayan"},
    {"person_id": 2, "name": "V D Satheesan"},
    {"person_id": 3, "name": "Suresh Gopi"},
]


class TestFetchPersonRoster(unittest.TestCase):
    def test_reduces_the_cache_payload_to_id_and_name(self) -> None:
        cache = {
            "version_id": 9,
            "persons": [
                {"person_id": 1, "name": "Pinarayi Vijayan", "party": "CPI(M)", "alliance": "LDF"},
                {"person_id": 2, "name": "V D Satheesan", "party": "INC", "alliance": "UDF"},
            ],
            "parties": [],
        }

        with patch("modules.extract_persons.fetch_api", return_value=cache) as fetch_api:
            roster = fetch_person_roster()

        fetch_api.assert_called_once_with("https://poli-engine-backend.onrender.com/cache")
        self.assertEqual(roster, [
            {"person_id": 1, "name": "Pinarayi Vijayan"},
            {"person_id": 2, "name": "V D Satheesan"},
        ])

    def test_skips_rows_with_no_usable_identity(self) -> None:
        cache = {"persons": [
            {"person_id": 1, "name": "Pinarayi Vijayan"},
            {"person_id": None, "name": "Ghost"},
            {"person_id": 4, "name": ""},
        ]}

        with patch("modules.extract_persons.fetch_api", return_value=cache):
            self.assertEqual(fetch_person_roster(), [{"person_id": 1, "name": "Pinarayi Vijayan"}])


class TestExtractPersons(unittest.TestCase):
    def _run(self, response):
        with patch("modules.extract_persons.load_prompt", return_value="Persons prompt"):
            with patch("modules.extract_persons.llm_node", return_value=response) as llm_node:
                result = extract_persons("മലയാളം ഉള്ളടക്കം", ROSTER)
        return result, llm_node

    def test_returns_the_ids_the_model_identified(self) -> None:
        result, llm_node = self._run(json.dumps({"person_ids": [1, 3]}))

        self.assertEqual(result, [1, 3])
        prompt = llm_node.call_args.kwargs["prompt"]
        self.assertIn("Persons prompt", prompt)
        # The roster must be in the prompt: the text is Malayalam, the names English.
        self.assertIn("Pinarayi Vijayan", prompt)
        self.assertIn("മലയാളം ഉള്ളടക്കം", prompt)

    def test_invented_ids_are_dropped(self) -> None:
        # A hallucinated id would attach a real person to an incident they are
        # not in, so only roster ids may survive.
        result, _ = self._run(json.dumps({"person_ids": [1, 999, 42]}))
        self.assertEqual(result, [1])

    def test_handles_fenced_json_and_a_bare_list(self) -> None:
        self.assertEqual(self._run('```json\n{"person_ids": [2]}\n```')[0], [2])
        self.assertEqual(self._run(json.dumps([2, 3]))[0], [2, 3])

    def test_numeric_strings_are_coerced_and_booleans_rejected(self) -> None:
        self.assertEqual(self._run(json.dumps({"person_ids": ["2", True, 3]}))[0], [2, 3])

    def test_duplicates_are_collapsed(self) -> None:
        self.assertEqual(self._run(json.dumps({"person_ids": [1, 1, 2]}))[0], [1, 2])

    def test_unparseable_response_yields_no_people(self) -> None:
        # Fails closed: an incident with nobody attached is incomplete, but the
        # wrong person attached is a false claim about a real individual.
        self.assertEqual(self._run("I could not determine this")[0], [])

    def test_llm_failure_does_not_propagate(self) -> None:
        with patch("modules.extract_persons.load_prompt", return_value="Persons prompt"):
            with patch("modules.extract_persons.llm_node", side_effect=RuntimeError("provider down")):
                self.assertEqual(extract_persons("content", ROSTER), [])

    def test_empty_content_or_roster_skips_the_model(self) -> None:
        with patch("modules.extract_persons.llm_node") as llm_node:
            self.assertEqual(extract_persons("", ROSTER), [])
            self.assertEqual(extract_persons("content", []), [])
        llm_node.assert_not_called()


if __name__ == "__main__":
    unittest.main()

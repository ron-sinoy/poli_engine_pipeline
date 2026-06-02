import sys
import unittest
from io import StringIO
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import patch

openai_stub = ModuleType("openai")
openai_stub.OpenAI = object
sys.modules.setdefault("openai", openai_stub)

from modules.llm_node import llm_node
from modules.config import DEFAULT_OPENROUTER_MODELS


def _response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ],
    )


class TestLlmNode(unittest.TestCase):
    def test_gemini_primary_success_skips_openrouter(self) -> None:
        with patch("modules.providers.llm.generate_gemini_response", return_value="gemini response"):
            with patch("modules.providers.llm.generate_openrouter_response") as openrouter_response:
                with patch("sys.stdout", new_callable=StringIO) as output:
                    response = llm_node("hello")

        self.assertEqual(response, "gemini response")
        openrouter_response.assert_not_called()
        self.assertEqual(output.getvalue(), "")

    def test_fallback_chain_uses_openrouter_models(self) -> None:
        calls = []

        def create(**request_body):
            calls.append(request_body["model"])
            if len(calls) < 3:
                raise RuntimeError("provider failed")
            return _response("final response")

        fake_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            ),
        )

        with patch("modules.providers.llm.generate_gemini_response", side_effect=RuntimeError("gemini failed")):
            with patch("modules.providers.openrouter.get_openrouter_api_key", return_value="test-key"):
                with patch("modules.providers.openrouter.OpenAI", return_value=fake_client):
                    with patch("sys.stdout", new_callable=StringIO) as output:
                        response = llm_node("hello")

        self.assertEqual(response, "final response")
        self.assertEqual(
            calls,
            DEFAULT_OPENROUTER_MODELS[:3],
        )
        self.assertIn(
            f"OpenRouter trying model: {DEFAULT_OPENROUTER_MODELS[0]}",
            output.getvalue(),
        )
        self.assertIn(
            "Gemini primary failed, falling back to OpenRouter: gemini failed",
            output.getvalue(),
        )
        self.assertIn(
            f"OpenRouter model failed: {DEFAULT_OPENROUTER_MODELS[0]} - provider failed",
            output.getvalue(),
        )
        self.assertIn(
            f"OpenRouter model succeeded: {DEFAULT_OPENROUTER_MODELS[2]}",
            output.getvalue(),
        )

    def test_first_model_success_logs_attempt_and_success(self) -> None:
        def create(**request_body):
            return _response("first response")

        fake_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            ),
        )

        with patch("modules.providers.llm.generate_gemini_response", side_effect=RuntimeError("gemini failed")):
            with patch("modules.providers.openrouter.get_openrouter_api_key", return_value="test-key"):
                with patch("modules.providers.openrouter.OpenAI", return_value=fake_client):
                    with patch("sys.stdout", new_callable=StringIO) as output:
                        response = llm_node("hello")

        self.assertEqual(response, "first response")
        self.assertIn(
            f"OpenRouter trying model: {DEFAULT_OPENROUTER_MODELS[0]}",
            output.getvalue(),
        )
        self.assertIn(
            f"OpenRouter model succeeded: {DEFAULT_OPENROUTER_MODELS[0]}",
            output.getvalue(),
        )

    def test_explicit_model_disables_fallback_chain(self) -> None:
        calls = []

        def create(**request_body):
            calls.append(request_body["model"])
            return _response("single model response")

        fake_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            ),
        )

        with patch("modules.providers.llm.generate_gemini_response", side_effect=RuntimeError("gemini failed")):
            with patch("modules.providers.openrouter.get_openrouter_api_key", return_value="test-key"):
                with patch("modules.providers.openrouter.OpenAI", return_value=fake_client):
                    with patch("sys.stdout", new_callable=StringIO) as output:
                        response = llm_node("hello", model="openai/gpt-4o-mini")

        self.assertEqual(response, "single model response")
        self.assertEqual(calls, [DEFAULT_OPENROUTER_MODELS[0]])
        self.assertIn(f"OpenRouter trying model: {DEFAULT_OPENROUTER_MODELS[0]}", output.getvalue())
        self.assertIn(f"OpenRouter model succeeded: {DEFAULT_OPENROUTER_MODELS[0]}", output.getvalue())

    def test_all_models_failed_logs_each_failure(self) -> None:
        def create(**request_body):
            return _response("")

        fake_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            ),
        )

        with patch("modules.providers.llm.generate_gemini_response", side_effect=RuntimeError("gemini failed")):
            with patch("modules.providers.openrouter.get_openrouter_api_key", return_value="test-key"):
                with patch("modules.providers.openrouter.OpenAI", return_value=fake_client):
                    with patch("sys.stdout", new_callable=StringIO) as output:
                        with self.assertRaisesRegex(RuntimeError, "OpenRouter response failed"):
                            llm_node("hello")

        self.assertIn(
            f"OpenRouter model failed: {DEFAULT_OPENROUTER_MODELS[0]} - empty content",
            output.getvalue(),
        )
        for model in DEFAULT_OPENROUTER_MODELS[1:]:
            self.assertIn(
                f"OpenRouter model failed: {model} - empty content",
                output.getvalue(),
            )

    def test_missing_openrouter_api_key_raises_clear_error(self) -> None:
        with patch("modules.providers.llm.generate_gemini_response", side_effect=RuntimeError("gemini failed")):
            with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}):
                with self.assertRaisesRegex(ValueError, "OPENROUTER_API_KEY is required"):
                    llm_node("hello", model="openai/gpt-4o-mini")


if __name__ == "__main__":
    unittest.main()

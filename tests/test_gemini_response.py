import unittest
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from modules.providers.gemini import generate_gemini_response


class TestGeminiResponse(unittest.TestCase):
    def test_generates_text_response(self) -> None:
        captured = {}

        def generate_content(**request_body):
            captured.update(request_body)
            return SimpleNamespace(text="gemini response")

        fake_client = SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content),
        )

        with patch("modules.providers.gemini.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini.genai.Client", return_value=fake_client):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    response = generate_gemini_response("hello")

        self.assertEqual(response, "gemini response")
        self.assertEqual(captured["model"], "gemini-2.0-flash")
        self.assertEqual(captured["contents"], "hello")
        self.assertIn("Gemini model succeeded: gemini-2.0-flash", output.getvalue())

    def test_generation_config_is_forwarded(self) -> None:
        captured = {}

        def generate_content(**request_body):
            captured.update(request_body)
            return SimpleNamespace(text="configured response")

        fake_client = SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content),
        )

        with patch("modules.providers.gemini.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini.genai.Client", return_value=fake_client):
                response = generate_gemini_response(
                    "hello",
                    temperature=0.2,
                    max_output_tokens=100,
                    top_p=0.9,
                    top_k=20,
                )

        self.assertEqual(response, "configured response")
        self.assertEqual(
            captured["config"],
            {
                "temperature": 0.2,
                "max_output_tokens": 100,
                "top_p": 0.9,
                "top_k": 20,
            },
        )

    def test_empty_response_raises_clear_error(self) -> None:
        def generate_content(**request_body):
            return SimpleNamespace(text="")

        fake_client = SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content),
        )

        with patch("modules.providers.gemini.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini.genai.Client", return_value=fake_client):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    with self.assertRaisesRegex(ValueError, "empty content"):
                        generate_gemini_response("hello")

        self.assertIn("Gemini model failed: gemini-2.0-flash - empty content", output.getvalue())

    def test_missing_gemini_api_key_raises_clear_error(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY is required"):
                generate_gemini_response("hello")


if __name__ == "__main__":
    unittest.main()

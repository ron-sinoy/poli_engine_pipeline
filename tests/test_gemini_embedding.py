import sys
import unittest
from io import StringIO
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import patch

google_stub = ModuleType("google")
genai_stub = ModuleType("google.genai")
genai_stub.Client = object
google_stub.genai = genai_stub
sys.modules.setdefault("google", google_stub)
sys.modules.setdefault("google.genai", genai_stub)

from modules.providers.gemini_embedding import generate_gemini_embedding


def _response(embedding: list[float]) -> SimpleNamespace:
    return SimpleNamespace(
        embeddings=[
            SimpleNamespace(
                values=embedding,
            )
        ],
    )


class TestGeminiEmbedding(unittest.TestCase):
    def test_embeds_dict_as_json_document(self) -> None:
        captured = {}

        def embed_content(**request_body):
            captured.update(request_body)
            return _response([0.1, 0.2])

        fake_client = SimpleNamespace(
            models=SimpleNamespace(embed_content=embed_content),
        )

        with patch("modules.providers.gemini_embedding.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini_embedding.genai.Client", return_value=fake_client):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    embedding = generate_gemini_embedding({"b": 2, "a": 1})

        self.assertEqual(embedding, [0.1, 0.2])
        self.assertEqual(captured["model"], "gemini-embedding-001")
        self.assertEqual(captured["contents"], '{"a": 1, "b": 2}')
        self.assertIn(
            "Gemini embedding model succeeded: gemini-embedding-001",
            output.getvalue(),
        )

    def test_embeds_string_directly(self) -> None:
        captured = {}

        def embed_content(**request_body):
            captured.update(request_body)
            return _response([0.3])

        fake_client = SimpleNamespace(
            models=SimpleNamespace(embed_content=embed_content),
        )

        with patch("modules.providers.gemini_embedding.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini_embedding.genai.Client", return_value=fake_client):
                embedding = generate_gemini_embedding("plain text")

        self.assertEqual(embedding, [0.3])
        self.assertEqual(captured["contents"], "plain text")

    def test_explicit_model_override_is_used(self) -> None:
        captured = {}

        def embed_content(**request_body):
            captured.update(request_body)
            return _response([0.4])

        fake_client = SimpleNamespace(
            models=SimpleNamespace(embed_content=embed_content),
        )

        with patch("modules.providers.gemini_embedding.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini_embedding.genai.Client", return_value=fake_client):
                embedding = generate_gemini_embedding("plain text", model="text-embedding-004")

        self.assertEqual(embedding, [0.4])
        self.assertEqual(captured["model"], "text-embedding-004")

    def test_empty_embedding_logs_failure(self) -> None:
        def embed_content(**request_body):
            return _response([])

        fake_client = SimpleNamespace(
            models=SimpleNamespace(embed_content=embed_content),
        )

        with patch("modules.providers.gemini_embedding.get_gemini_api_key", return_value="test-key"):
            with patch("modules.providers.gemini_embedding.genai.Client", return_value=fake_client):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    with self.assertRaisesRegex(ValueError, "empty embedding"):
                        generate_gemini_embedding("plain text")

        self.assertIn(
            "Gemini embedding model failed: gemini-embedding-001 - empty embedding",
            output.getvalue(),
        )

    def test_missing_gemini_api_key_raises_clear_error(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY is required"):
                generate_gemini_embedding("plain text")


if __name__ == "__main__":
    unittest.main()

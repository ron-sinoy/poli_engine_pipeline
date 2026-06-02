import sys
import unittest
from io import StringIO
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import patch

openai_stub = ModuleType("openai")
openai_stub.OpenAI = object
sys.modules.setdefault("openai", openai_stub)

from modules.providers.openrouter_embedding import generate_openrouter_embedding


def _response(embedding: list[float]) -> SimpleNamespace:
    return SimpleNamespace(
        data=[
            SimpleNamespace(
                embedding=embedding,
            )
        ],
    )


class TestOpenRouterEmbedding(unittest.TestCase):
    def test_embeds_dict_as_json_document(self) -> None:
        captured = {}

        def create(**request_body):
            captured.update(request_body)
            return _response([0.1, 0.2])

        fake_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=create),
        )

        with patch("modules.providers.openrouter_embedding.get_openrouter_api_key", return_value="test-key"):
            with patch("modules.providers.openrouter_embedding.OpenAI", return_value=fake_client):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    embedding = generate_openrouter_embedding({"b": 2, "a": 1})

        self.assertEqual(embedding, [0.1, 0.2])
        self.assertEqual(captured["model"], "openai/text-embedding-3-small")
        self.assertEqual(captured["input"], '{"a": 1, "b": 2}')
        self.assertIn(
            "OpenRouter embedding model succeeded: openai/text-embedding-3-small",
            output.getvalue(),
        )

    def test_embeds_list_as_one_json_document(self) -> None:
        captured = {}

        def create(**request_body):
            captured.update(request_body)
            return _response([0.3])

        fake_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=create),
        )

        with patch("modules.providers.openrouter_embedding.get_openrouter_api_key", return_value="test-key"):
            with patch("modules.providers.openrouter_embedding.OpenAI", return_value=fake_client):
                embedding = generate_openrouter_embedding([{"id": 1}, {"id": 2}])

        self.assertEqual(embedding, [0.3])
        self.assertEqual(captured["input"], '[{"id": 1}, {"id": 2}]')

    def test_embeds_string_directly(self) -> None:
        captured = {}

        def create(**request_body):
            captured.update(request_body)
            return _response([0.4])

        fake_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=create),
        )

        with patch("modules.providers.openrouter_embedding.get_openrouter_api_key", return_value="test-key"):
            with patch("modules.providers.openrouter_embedding.OpenAI", return_value=fake_client):
                embedding = generate_openrouter_embedding("plain text")

        self.assertEqual(embedding, [0.4])
        self.assertEqual(captured["input"], "plain text")

    def test_explicit_model_override_is_used(self) -> None:
        captured = {}

        def create(**request_body):
            captured.update(request_body)
            return _response([0.5])

        fake_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=create),
        )

        with patch("modules.providers.openrouter_embedding.get_openrouter_api_key", return_value="test-key"):
            with patch("modules.providers.openrouter_embedding.OpenAI", return_value=fake_client):
                embedding = generate_openrouter_embedding("plain text", model="qwen/qwen3-embedding-4b")

        self.assertEqual(embedding, [0.5])
        self.assertEqual(captured["model"], "qwen/qwen3-embedding-4b")

    def test_empty_embedding_logs_failure(self) -> None:
        def create(**request_body):
            return _response([])

        fake_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=create),
        )

        with patch("modules.providers.openrouter_embedding.get_openrouter_api_key", return_value="test-key"):
            with patch("modules.providers.openrouter_embedding.OpenAI", return_value=fake_client):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    with self.assertRaisesRegex(ValueError, "empty embedding"):
                        generate_openrouter_embedding("plain text")

        self.assertIn(
            "OpenRouter embedding model failed: openai/text-embedding-3-small - empty embedding",
            output.getvalue(),
        )

    def test_missing_openrouter_api_key_raises_clear_error(self) -> None:
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "OPENROUTER_API_KEY is required"):
                generate_openrouter_embedding("plain text")


if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path

from modules.llm_node import llm_node
from modules.prompt_loader import load_prompt
from modules.providers import generate_gemini_embedding


PROJECT_ROOT = Path(__file__).resolve().parent
SILVER_LEVEL_PATH = PROJECT_ROOT / "results" / "results_silver_level.json"


def load_silver_level_data() -> object:
    return json.loads(SILVER_LEVEL_PATH.read_text(encoding="utf-8"))


def build_prompt_with_silver_data(prompt_name: str) -> str:
    prompt = load_prompt(prompt_name)
    silver_level_data = load_silver_level_data()
    silver_level_json = json.dumps(silver_level_data, ensure_ascii=False, indent=2)
    return f"{prompt}\n\nsilver_level_data:\n{silver_level_json}"


def create_embedding_with_silver_data() -> list[float]:
    silver_level_data = load_silver_level_data()
    embedding = generate_gemini_embedding(silver_level_data)
    print(f"Embedding vector length: {len(embedding)}")
    return embedding


def test_embedding_with_silver_data() -> list[float]:
    return create_embedding_with_silver_data()


def main() -> None:
    response = llm_node(
        prompt=build_prompt_with_silver_data("thread_metadata_prompt.txt")
    )
    print(response)

if __name__ == "__main__":
    main()

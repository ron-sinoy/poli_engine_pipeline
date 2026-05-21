import json
from pathlib import Path

from medallion.bronze_level import build_bronze_level_data
from medallion.gold_level import (
    build_final_gold_data,
    build_initial_classification_gold_data,
)
from medallion.silver_level import build_silver_level_data
from modules.insert_results_gold import write_json_file
from modules.post_incidents import post_final_gold_incidents


BRONZE_RESULTS_PATH = Path("results/bronze_results.md")
SILVER_RESULTS_PATH = Path("results/silver_results.md")
INITIAL_GOLD_RESULTS_PATH = Path("results/initial_classification_gold.json")
FINAL_GOLD_RESULTS_PATH = Path("results/final_gold.json")


def main():
    bronze_level_data = build_bronze_level_data()
    silver_level_data = build_silver_level_data(bronze_level_data)
    write_json_markdown(BRONZE_RESULTS_PATH, bronze_level_data)
    write_json_markdown(SILVER_RESULTS_PATH, silver_level_data)

    if _should_end_pipeline_after_silver(silver_level_data):
        initial_classification_gold_data: object = {}
        final_gold_data: object = {}
        posted_incidents: list[object] = []
        write_json_file(INITIAL_GOLD_RESULTS_PATH, initial_classification_gold_data)
        write_json_file(FINAL_GOLD_RESULTS_PATH, final_gold_data)
        return (
            bronze_level_data,
            silver_level_data,
            initial_classification_gold_data,
            final_gold_data,
            posted_incidents,
        )

    initial_classification_gold_data = build_initial_classification_gold_data(
        silver_level_data
    )
    final_gold_data = build_final_gold_data(initial_classification_gold_data)
    write_json_file(INITIAL_GOLD_RESULTS_PATH, initial_classification_gold_data)
    write_json_file(FINAL_GOLD_RESULTS_PATH, final_gold_data)
    posted_incidents = post_final_gold_incidents(final_gold_data)

    return (
        bronze_level_data,
        silver_level_data,
        initial_classification_gold_data,
        final_gold_data,
        posted_incidents,
    )


def write_json_markdown(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write("```json\n")
        file.write(json.dumps(payload, indent=2, ensure_ascii=False))
        file.write("\n```")


def _should_end_pipeline_after_silver(payload: object) -> bool:
    if payload is None:
        return True

    if isinstance(payload, (list, dict, str)):
        return len(payload) == 0

    return False


if __name__ == "__main__":
    main()
    print(
        "results/bronze_results.md, results/silver_results.md, "
        "results/initial_classification_gold.json, and results/final_gold.json "
        "created successfully"
    )

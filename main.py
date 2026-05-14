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
from modules.progress_log import describe_payload, log_step


BRONZE_RESULTS_PATH = Path("results/bronze_results.md")
SILVER_RESULTS_PATH = Path("results/silver_results.md")
INITIAL_GOLD_RESULTS_PATH = Path("results/initial_classification_gold.json")
FINAL_GOLD_RESULTS_PATH = Path("results/final_gold.json")


def main():
    log_step("Starting main pipeline run.")
    bronze_level_data = build_bronze_level_data()
    log_step(f"Bronze stage completed with {describe_payload(bronze_level_data)}.")
    silver_level_data = build_silver_level_data(bronze_level_data)
    log_step(f"Silver stage completed with {describe_payload(silver_level_data)}.")
    log_step(f"Writing bronze markdown to {BRONZE_RESULTS_PATH}.")
    write_json_markdown(BRONZE_RESULTS_PATH, bronze_level_data)
    log_step(f"Finished writing bronze markdown to {BRONZE_RESULTS_PATH}.")
    log_step(f"Writing silver markdown to {SILVER_RESULTS_PATH}.")
    write_json_markdown(SILVER_RESULTS_PATH, silver_level_data)
    log_step(f"Finished writing silver markdown to {SILVER_RESULTS_PATH}.")

    if _should_end_pipeline_after_silver(silver_level_data):
        log_step(
            "Silver stage output was blank after checking; ending pipeline before gold stages."
        )
        initial_classification_gold_data: object = {}
        final_gold_data: object = {}
        posted_incidents: list[object] = []
        log_step(f"Writing initial gold JSON to {INITIAL_GOLD_RESULTS_PATH}.")
        write_json_file(INITIAL_GOLD_RESULTS_PATH, initial_classification_gold_data)
        log_step(f"Finished writing initial gold JSON to {INITIAL_GOLD_RESULTS_PATH}.")
        log_step(f"Writing final gold JSON to {FINAL_GOLD_RESULTS_PATH}.")
        write_json_file(FINAL_GOLD_RESULTS_PATH, final_gold_data)
        log_step(f"Finished writing final gold JSON to {FINAL_GOLD_RESULTS_PATH}.")
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
    log_step(
        "Initial gold stage completed with "
        f"{describe_payload(initial_classification_gold_data)}."
    )
    final_gold_data = build_final_gold_data(initial_classification_gold_data)
    log_step(f"Final gold stage completed with {describe_payload(final_gold_data)}.")

    log_step(f"Writing initial gold JSON to {INITIAL_GOLD_RESULTS_PATH}.")
    write_json_file(INITIAL_GOLD_RESULTS_PATH, initial_classification_gold_data)
    log_step(f"Finished writing initial gold JSON to {INITIAL_GOLD_RESULTS_PATH}.")
    log_step(f"Writing final gold JSON to {FINAL_GOLD_RESULTS_PATH}.")
    write_json_file(FINAL_GOLD_RESULTS_PATH, final_gold_data)
    log_step(f"Finished writing final gold JSON to {FINAL_GOLD_RESULTS_PATH}.")
    posted_incidents = post_final_gold_incidents(final_gold_data)
    log_step(
        "Incident posting step completed with "
        f"{describe_payload(posted_incidents)}."
    )

    return (
        bronze_level_data,
        silver_level_data,
        initial_classification_gold_data,
        final_gold_data,
        posted_incidents,
    )


def write_json_markdown(path: Path, payload: object) -> None:
    log_step(f"Preparing markdown JSON write for {path}.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write("```json\n")
        file.write(json.dumps(payload, indent=2, ensure_ascii=False))
        file.write("\n```")
    log_step(f"Markdown JSON write complete for {path}.")


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

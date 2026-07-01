import json
from pathlib import Path

from medallion.bronze_level import build_bronze_level_data
from medallion.gold_level import build_gold_level_data
from medallion.post_level import post_gold_level_data
from medallion.silver_level import build_silver_level_data
from modules.config import get_bronze_sources


BRONZE_RESULTS_PATH = Path("results/results_bronze_level.json")
SILVER_RESULTS_PATH = Path("results/results_silver_level.json")
PRE_POST_GOLD_RESULTS_PATH = Path("results/pre_post_gold_level.json")
MAIN_OUTPUT_GOLD_RESULTS_PATH = Path("results/main_output_gold.json")
SECONDARY_OUTPUT_GOLD_RESULTS_PATH = Path("results/secondary_output_gold.json")
GOLD_RESULTS_PATH = Path("results/results_gold_level.json")


def main():
    #MEDALLION ARCHITECTURE

    # 1.Bronze level
    bronze_sources = get_bronze_sources()   #get source,[url1,url2,..]
    bronze_level_data = build_bronze_level_data(bronze_sources)
    write_json_file(BRONZE_RESULTS_PATH, bronze_level_data)

    # 2.Silver level
    silver_level_data = build_silver_level_data(bronze_level_data)
    write_json_file(SILVER_RESULTS_PATH, silver_level_data)

    # 3.Gold level
    gold_level_data = build_gold_level_data(silver_level_data)
    write_json_file(PRE_POST_GOLD_RESULTS_PATH, gold_level_data)
    gold_post_data = post_gold_level_data(gold_level_data)
    write_json_file(MAIN_OUTPUT_GOLD_RESULTS_PATH, gold_post_data["main_output"])
    write_json_file(SECONDARY_OUTPUT_GOLD_RESULTS_PATH, gold_post_data["secondary_output"])
    write_json_file(GOLD_RESULTS_PATH, gold_post_data["combined"])
    return bronze_level_data, silver_level_data, gold_post_data
    


def write_json_file(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
    print(
        "results/results_bronze_level.json and "
        "results/results_silver_level.json and "
        "results/pre_post_gold_level.json and "
        "results/main_output_gold.json and "
        "results/secondary_output_gold.json and "
        "results/results_gold_level.json created successfully"
    )

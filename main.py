import json
from pathlib import Path

from medallion.bronze_level import build_bronze_level_data
from modules.config import get_bronze_sources


BRONZE_RESULTS_PATH = Path("results/results_bronze_level.json")


def main():
    #MEDALLION ARCHITECTURE

    # 1.Bronze level
    bronze_sources = get_bronze_sources()   #get source,[url1,url2,..]
    bronze_level_data = build_bronze_level_data(bronze_sources)
    write_json_file(BRONZE_RESULTS_PATH, bronze_level_data)
    return bronze_level_data


def write_json_file(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
    print("results/results_bronze_level.json created successfully")

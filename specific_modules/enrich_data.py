from modules.fetch_api import fetch_api
from modules.filter_json import filter_json_values


def enrich_data(source: str, item_detail_url: str) -> str:
    enriched_data: list[str] = []

    if source == "mathrubhumi":
        detail_payload = fetch_api(item_detail_url)

        for detail_item in detail_payload["detail_elements"]:
            if filter_json_values(detail_item, "elementType", [0, 1]):
                enriched_data.append(detail_item["elementContent"])

    return " ".join(enriched_data)

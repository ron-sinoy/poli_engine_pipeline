def complete_url(source: str, item_detail_url: str) -> str:
    if source == "mathrubhumi":
        return f"https://www.mathrubhumi.com{item_detail_url}"

    return item_detail_url

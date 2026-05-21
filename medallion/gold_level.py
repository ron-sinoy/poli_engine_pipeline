from typing import Any

from specific_modules.classify_gold_level_data import classify_gold_level_data
from specific_modules.finalize_gold_level_data import finalize_gold_level_data


def build_initial_classification_gold_data(silver_level_data: Any) -> Any:
    """Run the first gold-stage LLM pass over silver-level items."""
    return classify_gold_level_data(silver_level_data)


def build_final_gold_data(initial_classification_gold_data: Any) -> Any:
    """Run the second gold-stage LLM pass using thread details and cache."""
    return finalize_gold_level_data(initial_classification_gold_data)

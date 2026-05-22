from typing import Any

def merge_data(data1: Any, data2: Any) -> Any:
    """Merge two JSON values into a new value.

    - dict + dict: merge top-level keys, where ``data2`` overrides duplicates.
    - list + list: concatenate both lists in order.
    """
    
    #optional code, in future cases if the data after filtering top keys is 
    #a dict, not a list as current workflow.
    if isinstance(data1, dict) and isinstance(data2, dict):
        merged = dict(data1)
        merged.update(data2)
        return merged

    if isinstance(data1, list) and isinstance(data2, list):
        return [*data1, *data2]

    raise TypeError("merge_data expects both inputs to be dicts or both to be lists")

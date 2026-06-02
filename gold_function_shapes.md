# Gold Function Shapes

This document lists the gold pipeline steps from 1 through the current step 19b and records the output shape for each step.

## Step 1 - Load the translation prompt

Function: `_build_translation_prompt`

Output shape:

```json
"string"
```

## Step 2 - Build the silver-item translation prompt

Function: `_build_translation_prompt`

Output shape:

```json
"string"
```

## Step 3 - Send the prompt to the LLM and parse the JSON response

Functions: `_translate_silver_item`, `_parse_json_response`

Output shape:

```json
{
  "itemTitle": "string",
  "itemTitleLead": "string",
  "relatedStoriesTopic": "string",
  "content": "string",
  "source_id": "string"
}
```

## Step 4 - Build the embedding input

Function: `_build_embedding_input`

Output shape:

```json
{
  "itemTitle": "string",
  "itemTitleLead": "string",
  "relatedStoriesTopic": "string",
  "content": "string"
}
```

## Step 5 - Fetch `threadsInternal`

Function: `_fetch_threads_internal`

Output shape:

```json
[
  {
    "thread_id": "string",
    "title": "string",
    "summary": "string",
    "thread_vectors": [[0.0, 0.0]]
  }
]
```

## Step 6 - Normalize backend threads into a vectors list

Function: `_build_threads_vectors_list`

Output shape:

```json
[
  {
    "thread_id": "string",
    "title": "string",
    "summary": "string",
    "thread_vectors": [[0.0, 0.0]]
  }
]
```

## Step 7 - Generate the embedding and build the gold vector record

Function: `build_gold_level_data`

Output shape:

```json
[
  {
    "source_id": "string",
    "vector": [0.0, 0.0]
  }
]
```

## Step 8 - Build the vector-comparison batch

Functions: `build_compare_vectors_data`, `top_n_threads_classifier`

Output shape:

```json
[
  {
    "source_id": "string",
    "vector": [0.0, 0.0],
    "Threads": [
      {
        "thread_id": "string",
        "title": "string",
        "scores": 0.9,
        "summary": "string"
      }
    ]
  }
]
```

## Step 9 - Classify top matching threads

Function: `top_n_threads_classifier`

Output shape:

```json
[
  {
    "thread_id": "string",
    "title": "string",
    "scores": 0.9,
    "summary": "string"
  }
]
```

## Step 10 - Build the matched gold record

Function: `build_compare_vectors_data`

Output shape:

```json
[
  {
    "source_id": "string",
    "vector": [0.0, 0.0],
    "Threads": [
      {
        "thread_id": "string",
        "title": "string",
        "scores": 0.9,
        "summary": "string"
      }
    ]
  }
]
```

## Step 11 - Enrich the final gold record with silver incident fields

Functions: `_build_silver_lookup`, `_enrich_compared_data`

Output shape:

```json
[
  {
    "itemTitle": "string",
    "itemTitleLead": "string",
    "relatedStoriesTopic": "string",
    "content": "string",
    "source_id": "string",
    "vector": [0.0, 0.0],
    "Threads": [
      {
        "thread_id": "string",
        "title": "string",
        "scores": 0.9,
        "summary": "string"
      }
    ]
  }
]
```

## Step 12 - Classify the final gold records into political and non-political

Functions: `_classify_gold_items`, `_normalize_classifier_response`

Output shape:

```json
{
  "political": [
    {
      "para_content": "string",
      "source_id": "string",
      "thread_id": "string or null",
      "confidence_level": 0.9,
      "vector": [0.0, 0.0]
    }
  ],
  "non-political": ["source_id"]
}
```

## Step 13 - Mark all non-political source ids as filtered

Function: `_update_non_political_source_ids`

Output shape:

```json
null
```

## Step 14 - Return only political records

Function: `_extract_political_items`

Output shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "thread_id": "string or null",
    "confidence_level": 0.9,
    "vector": [0.0, 0.0]
  }
]
```

## Step 15 - Check political confidence and branch

Function: `confidence_checker`

Output shape:

```json
true
```

or

```json
false
```

## Step 16a - Confidence-pass branch

Function: `_reshape_political_items_for_thread_output`

Named output: `main_output`

Output shape:

```json
[
  {
    "source_id": "string",
    "thread_id": "string or null",
    "content": "string"
  }
]
```

## Step 16b - Build the failed-path payload

Function: failure branch in `build_gold_level_data`

Output shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "incidentList": [],
    "vector": [0.0, 0.0]
  }
]
```

## Step 17b - Load waiting-list incident vectors

Function: `vector_waiting_list_incidents`

Output shape:

```json
[
  {
    "id": 1,
    "vectors": [[0.0, 0.0]],
    "scores": 0.98
  }
]
```

## Step 18b - Compare the current vector with the waiting list

Function: `vector_waiting_list_incidents`

Output shape:

```json
[
  {
    "id": 1,
    "vectors": [[0.0, 0.0]],
    "scores": 0.98
  }
]
```

## Step 19b - Add content to waiting-list incidents and remove vectors

Functions: `content_waiting_list_incidents`, `_build_waiting_list_content_lookup`, `_enrich_failed_items_with_content`

Output shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "incidentList": [
      {
        "id": 1,
        "content": "string or null"
      }
    ],
    "vector": [0.0, 0.0]
  }
]
```

## Step 20b - Classify the waiting-list incidents against `para_content`

Functions: `_build_waiting_list_classification_prompt`, `_classify_waiting_list_items`, `_normalize_waiting_list_classification_response`

Output shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "vector": [0.0, 0.0],
    "incidentList": [
      {
        "id": 1,
        "content": "string",
        "confidence_score": 0.9
      },
      {
        "id": 2,
        "content": "string",
        "confidence_score": 0.8
      }
    ]
  }
]
```

## Step 21b - Check top-two waiting-list confidence scores

Function: `waiting_list_confidence_checker`

Output shape:

```json
true
```

or

```json
false
```

## Step 22bb - Post low-confidence waiting-list items

Function: `post_waitinglists`

Output shape:

```json
{
  "success": true
}
```

## Step 22ba - Reshape passing waiting-list items into thread candidates

Function: `_reshape_waiting_list_item_for_thread_creation`

Output shape:

```json
[
  {
    "source_id": "string",
    "content": "string",
    "thread_id": null
  },
  {
    "source_id": 1,
    "content": "string",
    "thread_id": null
  },
  {
    "source_id": 2,
    "content": "string",
    "thread_id": null
  }
]
```

## Step 23ba - Build thread title and summary from the three contents

Functions: `_build_waiting_list_thread_prompt`, `_generate_waiting_list_thread_metadata`

Output shape:

```json
[
  {
    "source_id": "string",
    "content": "string",
    "thread_id": null,
    "title": "string",
    "summary": "string"
  },
  {
    "source_id": 1,
    "content": "string",
    "thread_id": null,
    "title": "string",
    "summary": "string"
  },
  {
    "source_id": 2,
    "content": "string",
    "thread_id": null,
    "title": "string",
    "summary": "string"
  }
]
```

## Step 24ba - Create embedding with title and summary only

Function: `generate_gemini_embedding`

Output shape:

```json
[
  {
    "source_id": "string",
    "content": "string",
    "thread_id": null,
    "title": "string",
    "summary": "string"
  }
]
```

Note:
- embedding is internal only and not returned

## Step 25ba - Post threads and stamp the returned thread id

Function: `post_threads`

Named output: `secondary_output`

Output shape:

```json
[
  {
    "source_id": "string",
    "content": "string",
    "thread_id": 11
  },
  {
    "source_id": 1,
    "content": "string",
    "thread_id": 11
  },
  {
    "source_id": 2,
    "content": "string",
    "thread_id": 11
  }
]
```

Note:

- `title` and `summary` are only used before `post_threads`
- they are not part of the returned `secondary_output`

## Final Gold Return

Saved outputs:

- `results/main_output_gold.json`
- `results/secondary_output_gold.json`
- `results/results_gold_level.json`

Current returned shape:

```json
{
  "main_output": [
    {
      "source_id": "string",
      "thread_id": "string or null",
      "content": "string"
    }
  ],
  "secondary_output": [
    {
      "source_id": "string",
      "thread_id": 11,
      "content": "string"
    }
  ],
  "combined": [
    {
      "source_id": "string",
      "thread_id": "string or null",
      "content": "string"
    },
    {
      "source_id": "string",
      "thread_id": 11,
      "content": "string"
    }
  ]
}
```

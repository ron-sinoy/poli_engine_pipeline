# Gold Flow Steps

This documents the current gold-stage flow as 18 steps, with the input shape for each step.

## Step 1 - Load the translation prompt

Params input shape:

```json
{
  "prompt_name": "prompt_translate.txt"
}
```

## Step 2 - Build the silver-item translation prompt

Params input shape:

```json
{
  "silver_item": {
    "itemTitle": "string",
    "itemTitleLead": "string",
    "relatedStoriesTopic": "string",
    "content": "string",
    "source_id": "string"
  }
}
```

## Step 3 - Send the prompt to the LLM and parse the JSON response

Params input shape:

```json
{
  "prompt": "string"
}
```

## Step 4 - Build the embedding input

Params input shape:

```json
{
  "translated_item": {
    "itemTitle": "string",
    "itemTitleLead": "string",
    "relatedStoriesTopic": "string",
    "content": "string",
    "source_id": "string"
  }
}
```

Note: `source_id` is removed before the embedding call.

## Step 5 - Fetch `threadsInternal`

Params input shape:

```json
{}
```

## Step 6 - Normalize backend threads into a vectors list

Params input shape:

```json
{
  "threads_internal": [
    {
      "thread_id": "string",
      "title": "string",
      "summary": "string",
      "thread_vectors": [[0.0, 0.0]]
    }
  ]
}
```

## Step 7 - Generate the embedding and build the gold vector record

Params input shape:

```json
{
  "embedding_input": {
    "itemTitle": "string",
    "itemTitleLead": "string",
    "relatedStoriesTopic": "string",
    "content": "string"
  }
}
```

## Step 8 - Build the vector-comparison batch

Params input shape:

```json
{
  "main_data": [
    {
      "source_id": "string",
      "vector": [0.0, 0.0]
    }
  ],
  "vectors_list": [
    {
      "thread_id": "string",
      "title": "string",
      "summary": "string",
      "thread_vectors": [[0.0, 0.0]]
    }
  ],
  "count": 3
}
```

## Step 9 - Classify top matching threads

Params input shape:

```json
{
  "vector_ref": [0.0, 0.0],
  "vectors_list": [
    {
      "thread_id": "string",
      "title": "string",
      "summary": "string",
      "thread_vectors": [[0.0, 0.0]]
    }
  ],
  "count": 3,
  "confidence_level": 0.5
}
```

## Step 10 - Build the matched gold record

Params input shape:

```json
{
  "item": {
    "source_id": "string",
    "vector": [0.0, 0.0]
  },
  "Threads": [
    {
      "thread_id": "string",
      "title": "string",
      "scores": 0.9,
      "summary": "string"
    }
  ]
}
```

## Step 11 - Enrich the final gold record with silver incident fields

Params input shape:

```json
{
  "compared_data": [
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
  ],
  "silver_level_data": [
    {
      "itemTitle": "string",
      "itemTitleLead": "string",
      "relatedStoriesTopic": "string",
      "content": "string",
      "source_id": "string"
    }
  ]
}
```

Final enriched output shape:

```json
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
```

Note: no extra silver fields are currently available at gold time beyond these five keys.

## Step 12 - Classify the final gold records into political and non-political

Params input shape:

```json
{
  "gold_level_items": [
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
}
```

Final output shape:

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

Params input shape:

```json
{
  "non-political": ["source_id"]
}
```

Side effect:

- call `sourceids/update` for each `source_id`
- send `status: "filtered"`

## Step 14 - Return only political records

Params input shape:

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
  ]
}
```

Final output shape:

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

## Step 20b - Classify the waiting-list incidents against `para_content`

Params input shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "vector": [0.0, 0.0],
    "incidentList": [
      {
        "id": 1,
        "content": "string"
      }
    ]
  }
]
```

Final output shape:

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

Params input shape:

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

Behavior:

- use `params.json` and the existing benchmark confidence value
- pass only when both top-two incident confidence scores are above the benchmark
- otherwise follow step 21bb

Final output shape:

```json
true
```

or

```json
false
```

## Step 22bb - Post low-confidence waiting-list items

Params input shape:

```json
{
  "content": "string",
  "vectors": [0.0, 0.0]
}
```

Behavior:

- call `POST /waitinglists`
- send the current `para_content` as `content`
- send the current `vector` as `vectors`

Final output shape:

```json
{
  "success": true
}
```

## Step 22ba - Reshape passing waiting-list items into thread candidates

Params input shape:

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

Final output shape:

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

Params input shape:

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

Final output shape:

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

Params input shape:

```json
{
  "title": "string",
  "summary": "string"
}
```

Final output shape:

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

- embedding is created internally with `title` and `summary`
- the vector is not added to the returned shape

## Step 25ba - Post threads and stamp the returned thread id

Named output: `secondary_output`

Params input shape:

```json
{
  "title": "string",
  "summary": "string"
}
```

Final output shape:

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

- `title` and `summary` are internal inputs to `post_threads`
- they are removed from the returned pipeline shape after posting

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

## Step 15 - Check political confidence and branch

Params input shape:

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

Behavior:

- call the confidence checker using the benchmark in `params.json`
- if confidence passes, follow route `16a`
- otherwise, follow route `16b`

## Step 16a - Confidence-pass reshaper

Named output: `main_output`

Params input shape:

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

Params input shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "thread_id": "string",
    "confidence_level": 0.9,
    "vector": [0.0, 0.0]
  }
]
```

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

Params input shape:

```json
{
  "vector": [0.0, 0.0]
}
```

Output shape:

```json
[
  {
    "id": 1,
    "vectors": [[0.0, 0.0]]
  }
]
```

## Step 18b - Compare the current vector with the waiting list

Params input shape:

```json
{
  "vector": [0.0, 0.0],
  "count_level_waiting_list_incidents": 3
}
```

Behavior:

- reuse the previous vector
- compare it with waiting-list incident vectors
- keep the top `n` from `params.json`
- output the selected incidents under `incidentList`

## Step 19b - Add content to waiting-list incidents and remove vectors

Params input shape:

```json
[
  {
    "para_content": "string",
    "source_id": "string",
    "incidentList": [
      {
        "id": 1,
        "vectors": [[0.0, 0.0]],
        "scores": 0.98
      }
    ],
    "vector": [0.0, 0.0]
  }
]
```

Behavior:

- load waiting-list content from `/content_waiting-list_incidents`
- match content by `id`
- add `content` to each `incidentList` item
- remove `vectors` from each `incidentList` item
- remove `scores` from each `incidentList` item

Final output shape:

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

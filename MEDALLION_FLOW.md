# Medallion Pipeline Flow

This document describes the executable flow in `medallion/` as it exists now. The run is orchestrated by `main.py`; `medallion/__init__.py` only re-exports the four public functions and contains no processing logic.

## Top-level flow (`main.py`)

```text
bronze_sources.json
  -> get_bronze_sources()
  -> Bronze
  -> results/results_bronze_level.json
  -> Silver
  -> results/results_silver_level.json
  -> [Silver empty?]
       Path A: write empty Gold result files and return
       Path B: Gold -> pre_post_gold_level.json -> Post -> final result files
```

### Path A — Silver is empty

`main.py` does not call Gold or Post when the Silver list is empty. It writes:

- `results/pre_post_gold_level.json` with empty `main_output`, `secondary_output`, `combined`, and `non_political_source_ids`
- `results/main_output_gold.json` as `[]`
- `results/secondary_output_gold.json` as `[]`
- `results/results_gold_level.json` as `[]`

Then it returns.

### Path B — Silver has at least one item

`main.py` calls `build_gold_level_data(silver_level_data)`, writes its result to `pre_post_gold_level.json`, then calls `post_gold_level_data(gold_level_data)`. The post result is written to the three final Gold files.

## Bronze (`medallion/bronze_level.py`)

Public function: `build_bronze_level_data(sources)`.

1. Start with an empty `bronze_level_data` list.
2. For each configured source and each of its API URLs:
   1. Fetch JSON using `fetch_api(url)`.
   2. Pass the payload to `filter_raw_data(source_name, payload)`.
      - Currently, only `mathrubhumi` is supported. Its filter returns `payload["home"]["data"]`; an unexpected payload returns `None`.
      - An unsupported source raises `ValueError`.
   3. Add `source: <source_name>` to every returned item.
   4. Merge the items into the accumulated list with `merge_data`.
3. Return the merged list. `main.py` writes it to `results/results_bronze_level.json`.

There is no intentional branching after a successful fetch. A malformed source payload, unsupported source, or fetch failure stops the run rather than producing a separate recovery path.

## Silver (`medallion/silver_level.py`)

Public function: `build_silver_level_data(bronze_level_data)`.

### Candidate selection

Each Bronze item must pass all three checks in `_relabel_candidates`:

1. `elementType` is `0` or `1`.
2. `sectionTitle` is `"News"`.
3. `subSectionTitle` is `"India"` or `"Kerala"`.

If any check fails, that item is skipped permanently for this run. A passing item is assigned a source ID using `relabel_source_id`; for Mathrubhumi this is `mt_#<contentID>`.

### Path A — Item fails a Silver content filter

The item is not a candidate and never reaches enrichment, the database, Gold, or Post.

### Path B — Item passes all Silver content filters

1. The pipeline sends all candidate source IDs in one request to `get_seen_source_ids`.
2. Each candidate gets a complete detail URL via `complete_url`.
3. `enrich_data` fetches the article detail payload and concatenates `elementContent` from detail elements whose `elementType` is `0` or `1`.
4. `insert_db(source_id)` posts the ID with status `processing`.
5. Only these keys are retained: `itemTitle`, `itemTitleLead`, `source_id`, `source_url`, `content`, `relatedStoriesTopic`.
6. The filtered record is appended to Silver.

### Duplicate-check diversion — current local code versus committed code

The source-ID lookup is still performed, but the actual skip is currently commented out:

```python
# if check_db(seen_source_ids, relabeled_item["source_id"]):
#     continue
```

Therefore, **in the current working tree**, a known source ID follows Path B and is reprocessed.

If those two lines are uncommented, the old/committed behaviour is:

### Path C — Candidate source ID already exists in the backend

`check_db(...)` returns true, `continue` executes, and the article is omitted from Silver. It is not enriched and is not inserted as `processing` again.

## Gold (`medallion/gold_level.py`)

Public function: `build_gold_level_data(silver_level_data)`.

### Common processing

For every Silver item:

1. Send the entire Silver item to the translation LLM prompt.
2. Parse the returned JSON.
3. Remove `source_id` from a copy of the translated item and generate a Gemini embedding from that copy.
4. Retain `{source_id, vector}` internally.
5. Send each vector to `match_threads`, which returns the ranked existing threads and cosine scores.
6. Reattach the original Silver fields (`itemTitle`, `itemTitleLead`, `relatedStoriesTopic`, `content`, `source_id`, `source_url`).
7. Send all enriched items to the political-classifier LLM.

The classifier response is normalized:

- Only dictionary entries in `political` are kept.
- A reported `thread_id` is accepted only if it is an integer (or numeric string) **and** exists in that item’s `match_threads` result. Its confidence is the database cosine score, never a model-supplied score.
- String source IDs, or objects containing `source_id`, from `non-political` / `non_political` are retained as non-political IDs.

### Path A — Classified non-political

The ID is returned in `non_political_source_ids`. It has no Gold incident output. Post later marks it `filtered`.

### Path B — Political item passes `confidence_checker`

The item becomes a main output item:

```json
{
  "source_id": "...",
  "thread_id": 123,
  "content": "<para_content>",
  "source_url": "..."
}
```

It is destined for an existing thread.

### Path C — Political item fails `confidence_checker`

1. If it has no vector, it is discarded from the secondary route.
2. Otherwise, query `vector_waiting_list_incidents(vector)` for similar waiting-list incidents.
3. Build a failed item containing its paraphrased content, source ID, source URL, vector, and the returned incidents.

If there are no failed items, `secondary_output` remains empty.

If there are failed items, each is passed through a second LLM classification step:

1. Only the first two matching incidents are shown to the LLM, with text truncated to 240 characters and without cosine scores.
2. The LLM can mark an incident related only with `is_related: true`.
3. The original database content, source URL, source ID, and cosine score are restored.
4. Unrelated/non-dictionary incidents are removed.
5. Related incidents are sorted by confidence score and capped at two.

These normalized failed items become `secondary_output`.

Gold returns:

```text
{
  main_output: [passed political items],
  secondary_output: [failed political items with up to two related waiting-list incidents],
  combined: main_output + secondary_output,
  non_political_source_ids: [IDs]
}
```

## Post (`medallion/post_level.py`)

Public function: `post_gold_level_data(gold_level_data)`.

1. Read `main_output`, `secondary_output`, and `non_political_source_ids` from the Gold result.
2. Mark every non-political source ID `filtered` through `update_db`.
3. Fetch the person roster once.
4. Process main output.
5. Process secondary output.

Whenever an incident is posted, the pipeline extracts people from its content using the fetched roster and posts the incident with those person links.

### Path A — Main output item

For each main item:

1. Post the incident to its selected existing `thread_id`.
2. Mark its source ID `completed`.
3. Include it in final `main_output`.

If either operation fails, the exception is printed, the item remains absent from final output, and processing continues with the next main item.

### Path B — Secondary item passes `waiting_list_confidence_checker`

This means the secondary item should create a new thread.

1. Make thread candidates: the new news item plus up to two related waiting-list incidents.
2. Ask the LLM for the new thread’s title and summary.
3. Embed that title/summary and create the thread with `post_threads`.
4. Assign the returned thread ID to every candidate.
5. Post the new article as an incident and mark its source ID `completed`.
6. For each promoted waiting-list incident:
   1. Post it to the new thread.
   2. Mark its waiting-list row `completed`.
   3. If it has a source ID, mark that source ID `completed`.
7. Return all posted candidates in final `secondary_output`.

### Path C — Secondary item fails `waiting_list_confidence_checker`

The item does not create a thread. The pipeline:

1. Posts it to the waiting list with content, vector, source URL, and source ID.
2. Marks the source ID `completed`.
3. Returns no final secondary item.

### Path D — A secondary-item operation fails

The exception is printed as `waiting list post failed ...`; the loop continues with the next secondary item. The failed item is not included in final output.

The returned post result is:

```text
{
  main_output: [successfully posted main incidents],
  secondary_output: [successfully posted new-thread candidates],
  combined: main_output + secondary_output
}
```

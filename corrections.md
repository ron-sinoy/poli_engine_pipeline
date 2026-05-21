# Corrections

## What is more

- The current silver stage does more than just `check against db`: it fetches existing `sourceids`, filters items by `contentID`, and then POSTs processed `sourceids` back to the backend. See `medallion/silver_level.py:20-31` and `modules/check_db.py:10-97`.
- The current silver stage also fetches each article detail payload from `itemDetailURL` and merges `detail_elements[].elementContent` into a `content` field before gold processing. See `specific_modules/enrich_silver_level_data.py:53-113`. This extra detail-fetch enrichment is not shown in the PDF flow.
- The current gold stage additionally fetches backend `cache` data and normalizes the final LLM output into `normalized_incidents` before posting. See `specific_modules/finalize_gold_level_data.py:21-57` and `modules/normalize_final_incidents.py`.
- The current pipeline writes intermediate result files for bronze, silver, initial gold, and final gold. See `main.py:27-31` and `main.py:65-74`. This output-writing layer is not shown in the PDF.

## What is missing

- The PDF shows separate `Source A` and `Source B` branches, but the current bronze stage only hardcodes two Mathrubhumi home APIs and merges them. There is no distinct per-source pipeline abstraction. See `medallion/bronze_level.py:9-23`.
- The PDF shows an explicit `confidence check` / `highest value below threshold` step after thread allocation. The current gold-1 flow has no confidence score, no threshold handling, and no low-confidence branch; it directly accepts the LLM classification or creates a new thread. See `specific_modules/classify_gold_level_data.py:16-53` and `specific_modules/resolve_missing_threads.py:18-80`.
- The PDF shows `If Empty -> Return 0`. The current pipeline does stop early on empty silver output, but it returns empty structures and writes empty gold files instead of returning `0`. See `main.py:34-53`.
- The PDF shows `isPolitical` as a separate gold-stage step. In the current code, that logic is not a standalone stage; it is folded into the first LLM prompt and partly pre-filtered earlier using section/subsection rules. See `prompts/prompt1.txt:1-6` and `specific_modules/filter_bronze_level_data.py:7-25`.

## Overall file architecture

- `main.py` is the orchestrator. It runs bronze, silver, gold-1, gold-2, writes result files, and posts final incidents.
- `medallion/` contains the stage-level entry functions: `bronze_level.py`, `silver_level.py`, and `gold_level.py`. These files define the high-level pipeline stages, not the low-level logic.
- `specific_modules/` contains stage-specific business logic. This is where bronze filtering, silver enrichment, gold classification, finalization, and new-thread resolution are implemented.
- `modules/` contains shared utilities and backend integrations, such as generic API fetches, DB/sourceid checks, thread creation, thread/cache fetches, LLM calls, result writing, and incident posting.
- `prompts/` contains the LLM instruction files used by the gold stages and thread creation flow.
- `results/` stores generated intermediate and final output artifacts from pipeline runs.

- Overall, the architecture is layered like this:
  `main.py` -> `medallion/` stage wrappers -> `specific_modules/` stage logic -> `modules/` shared helpers/backend calls.

## How completion and error messages run

- While the pipeline runs, it keeps printing update messages.
- If a step works, you see the next message.
- So the messages move like this:
  start pipeline -> bronze done -> silver done -> gold done -> files written -> incidents posted -> final success message
- If a small problem happens a- If a small problem happens and the code knows how to handle it, it prints that problem and continues.nd the code knows how to handle it, it prints that problem and continues.
- If a big problem happens and the code does not handle it, the pipeline stops at that point.
- If the pipeline stops, the final success message does not come.
- Gemini is a little different:
  if Gemini fails once, it retries
  so you may see attempt 1, attempt 2, waiting, and then either success or final failure
- Simple rule:
  messages keep coming = pipeline is still running
  messages stop suddenly = pipeline most likely failed there
  final success message appears = full pipeline completed

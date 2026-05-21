**Bronze**

1. Get json data via api
	- Merge all apis into one for a specific source, with same format
2. Remove unwanted
    
    - store raw HTML/text as-is without any processing
    - output is a list of raw article objects containing title, body, and source URL

**Silver**

1. Filter non-political
    
    - remove articles that have no relevance to politics
    - each article is checked against political keywords and context, non-matching articles are dropped
2. Remove duplicates
    
    - drop articles already seen in previous pipeline runs using source URL
    - source URL is checked against previously inserted incidents in Supabase to prevent reprocessing
3. Check if empty
    
    - verify if anything survived filtering
    - if the filtered list is empty the pipeline skips all remaining stages
4. Exit if empty
    
    - terminate pipeline early if silver output is blank
    - empty result files are written and pipeline returns without calling Gemini or the backend

**Embedding**

1. Compute embeddings
    - convert each article text into a vector using sentence-transformers locally
    - sentence-transformers runs on GitHub Actions runner, each article body is encoded into a 384-dimensional vector and stored alongside the article object

**Gold 1**

1. Fetch threadsList from backend
    
    - get all existing threads from Railway backend to compare against
    - GET /threadsList returns id, title, and summary for all threads, used as context for Gemini classification
2. Gemini isPolitical check
    
    - confirm article is political using Gemini before proceeding
    - article is passed to Gemini with a prompt asking for a boolean political relevance decision
3. Gemini thread match
    
    - ask Gemini which existing thread this article belongs to if any
    - thread list and article are passed together to Gemini which returns a matched thread id or null
4. Confidence check
    
    - if match confidence is below threshold send article to pending_entries instead
    - low confidence articles are inserted into pending_entries with their embedding for future clustering

**Gold 2**

1. Deduplication check
    
    - verify this specific incident does not already exist inside the matched thread
    - existing thread entries are compared against the new article to catch semantic duplicates Gemini may have missed
2. Paraphrase via Gemini
    
    - rewrite article content into a clean structured incident format
    - Gemini rewrites the raw article into a concise Malayalam-aware incident description
3. Structure final payload
    
    - assemble all fields required by the POST /incidents contract
    - thread_id, body, persons_involved, source_url, and is_breaking are assembled into the final JSON
4. Tag is_breaking
    
    - mark incident as breaking news for frontend surfacing
    - is_breaking is set to true for all freshly inserted incidents, expires after 24 hours

**Post**

1. POST /incidents to backend
    
    - send final structured payload to Railway backend for DB insertion
    - backend writes to Supabase via the CSR pattern, returns inserted incident id on success
2. Log pipeline run to Supabase
    
    - record run metadata including article count, incidents posted, duration, and status
    - pipeline_runs table receives a row with start time, end time, articles processed, incidents posted, and success or failure status
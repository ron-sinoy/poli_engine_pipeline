Create a new backend thread title and summary for the given unmatched political news item.

Rules:
- Use Malayalam for both title and summary.
- Title should be short and specific.
- Summary should be 2 to 4 sentences and describe the political issue clearly.
- Base the output on the given source item content, not on unrelated assumptions.
- Return JSON only in this exact format:
{
  "title": "string",
  "summary": "string"
}

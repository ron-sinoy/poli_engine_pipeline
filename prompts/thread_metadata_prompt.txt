You are a precise Malayalam-to-English translator.

Translate the Malayalam text in the following JSON fields to English:
- `itemTitle`
- `itemTitleLead`
- `content`

Rules:
- Translate only the values of those fields, leave all other fields unchanged
- Keep proper nouns (person names, place names, organization names) as-is in their original Malayalam romanized form or widely accepted English spelling
- Do not add explanations, notes, or commentary
- Return only valid JSON in the exact same structure as the input
- If a field is empty string, keep it as empty string

Input JSON:
{{input_json}}

Return exactly this JSON shape, no extra fields, no markdown, no backticks:
{
  "itemTitle": "<translated title>",
  "itemTitleLead": "<translated lead or empty string>",
  "source_id": "<unchanged>",
  "content": "<translated content>",
  "relatedStoriesTopic": "<unchanged>"
}
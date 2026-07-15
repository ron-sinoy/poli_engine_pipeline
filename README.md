# Poli Engine

Pipeline that turns scraped Malayalam political news into structured threads, timelines, incidents, and quotes.

## Pipeline

Mathrubhumi → Bronze (raw) → LLM structuring (OpenRouter) → Silver → Embeddings (Gemini `text-embedding-004`, 768-dim pgvector) → Gold (resolved threads) → Express API (Render) → React frontend

## Stack

- LLM: OpenRouter, Gemini Flash
- DB: Supabase / Postgres + pgvector
- Backend: Node/Express (Controller-Service-Repository), Render
- Frontend: React

**refer file architecture.pdf** - for full architecture view
<img width="1748" height="824" alt="image" src="https://github.com/user-attachments/assets/c5bd9969-6ec9-4f7a-875e-420d37250dd3" />
<img width="1748" height="824" alt="image" src="https://github.com/user-attachments/assets/c5514ebd-08db-4926-ac38-a40f45912365" />

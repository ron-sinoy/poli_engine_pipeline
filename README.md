# Poli Engine

Pipeline that turns scraped Malayalam political news into structured threads, timelines, incidents, and quotes.

## Pipeline

Mathrubhumi → Bronze (raw) → LLM structuring (OpenRouter) → Silver → Embeddings (Gemini `text-embedding-004`, 768-dim pgvector) → Gold (resolved threads) → Express API (Railway) → React frontend

## Stack

- LLM: OpenRouter, Gemini Flash
- DB: Supabase / Postgres + pgvector
- Backend: Node/Express (Controller-Service-Repository), Railway
- Frontend: React

**refer file architecture.pdf**

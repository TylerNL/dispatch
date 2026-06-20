# Dispatch

Dispatch is intended to be a centralized aggregation of tech news.

Start-up news, major AI labs, and other general tech information all condensed into one email. Additionally, Dispatch has a RAG system to answer questions over the same index w/ citations to answer any questions about articles or other general questions regarding the news listed.

## Repo layout

```
design.md                     landing-page spec (copy, tokens, component tree)
frontend/                     Vite + React + TypeScript + Tailwind — landing, auth, chat, profile
backend/                      FastAPI + SQLAlchemy + pgvector RAG service (see backend/README.md)
.github/workflows/ingest.yml  nightly ingestion cron
```

## Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, lucide-react, React Router
- **Backend:** Python 3.13, FastAPI, async SQLAlchemy, Postgres + pgvector, Alembic
- **Auth:** Supabase Auth (email/password + Google OAuth), JWT-verified on the API
- **Models:** OpenAI GPT-4.1 Nano (generation, classification, summaries) · `text-embedding-3-small` @ 1024-dim (embeddings)

## How it works

### Ingestion → index

Nightly, a scheduled GitHub Actions workflow (`.github/workflows/ingest.yml`) runs the pipeline across the live sources:

1. **Fetch** — TechCrunch, Hacker News, arXiv, and AI-lab blogs (Anthropic, OpenAI; DeepMind planned)
2. **Deduplicate** — URL-fingerprint check drops redundant articles before any LLM cost
3. **Summarize** — concise per-article summaries
4. **Classify** — topic + signal score, enabling fine-grained filtering downstream
5. **Embed & store** — chunk embeddings written into pgvector (HNSW, cosine)

### RAG chat

Hybrid retrieval with streamed, cited answers:

- **Vector search** — cosine similarity over HNSW-indexed chunk embeddings with a recency-decay penalty
- **Keyword search** — Postgres full-text search via `websearch_to_tsquery` over a GIN-indexed `tsvector` column (title weight A / summary weight B); supports natural-language queries, quoted phrases, and negation
- **Fusion** — Reciprocal Rank Fusion (RRF, k=60) over both ranked lists
- **Generation** — streamed (SSE) answers with inline `[n]` citations mapped back to source items

### Accounts & persistence

- **Auth** — Supabase sign-in (email/password + Google); the API verifies the Supabase JWT on every chat request
- **Chat history** — conversations are saved per user: deep-linkable (`/chat/:id`), restored on refresh, synced across devices, with model-generated titles (via same GPT model)
- **Profile** — editable display name and topic-preference selection


## Quick start

The frontend and backend run separately.

**Backend** (details in `backend/README.md`):

```bash
cd backend
uv sync
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Deployment TBD (To Be Deployed): planned via Vercel (frontend) + Render (backend).
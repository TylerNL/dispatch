# dispatch — backend

RAG backend for dispatch. Ingests tech-news sources, dedupes, summarizes, classifies, and embeds them into Postgres/pgvector; serves a streaming chat endpoint with citations and persisted per-user history; and builds a daily topic-grouped digest.

Generation, classification, and summaries run on OpenAI `gpt-4.1-nano`; embeddings on `text-embedding-3-small` @ 1024-dim truncated.

## Layout

```
app/
  main.py            FastAPI factory, CORS, router mounts
  config.py          settings (pydantic-settings) — all env vars
  api/
    auth.py          get_current_user — verifies Supabase JWT (ES256 via JWKS, HS256 fallback)
    ask.py           POST /ask (sync) + POST /ask/stream (SSE, persists turns)
    chats.py         conversation history CRUD (auth-scoped)
    digest.py        GET /digest/today + /digest/{date}
    sources.py       GET /sources (stub)
    health.py        GET /health
    debug.py         manual per-source ingest + POST /seed
  ingest/
    base.py          Source ABC — async fetch(since) -> AsyncIterator[Item]
    sources.py       source classes + REGISTRY + LIVE_SOURCES
    scheduler.py     pipeline orchestration (run_once/run_all) + `python -m app.ingest.scheduler`
  pipeline/
    dedupe.py        URL canonicalization + fingerprint check
    embed.py         OpenAI single + batch embeddings
    summarize.py     per-item summary (concurrency-bounded)
    classify.py      topic + signal score (concurrency-bounded)
  rag/
    retriever.py     hybrid search (vector + keyword via RRF) w/ window + topic filters
    generator.py     OpenAI call, sync + SSE streaming, citation handling
    titler.py        cheap conversation-title generation
    prompts.py       SYSTEM_PROMPT + context formatter
  storage/
    db.py            async engine + session dependency
    models.py        ItemRow, ChunkRow, SourceRow, SubscriberRow, ConversationRow, MessageRow
    vector.py        upsert, vector_search, keyword_search, recent_items, hydrate_items, search
    chats.py         ownership-scoped conversation/message CRUD
  digest/
    builder.py       build_for(day) + render_html/render_text (Pacific time)
    mailer.py        SMTP send + broadcast (stub)
  schemas/           Pydantic API types — source of truth for API shape
```

## API reference

Base path: `/api`. Auth is a Supabase access token passed as `Authorization: Bearer <token>`, verified by `app/api/auth.py`. Shapes below reference the Pydantic models in `app/schemas/`.

### Auth required

| Method | Path | Request | Response |
|---|---|---|---|
| POST | `/api/ask/stream` | `AskRequest` (**`conversation_id` required**) | `text/event-stream` — see SSE events below |
| GET | `/api/conversations` | — | `ConversationSummary[]`, newest first |
| GET | `/api/conversations/{id}` | — | `ConversationDetail` (404 if not owner) |
| PATCH | `/api/conversations/{id}` | `RenameRequest` | `204` (404 if not owner) |
| DELETE | `/api/conversations/{id}` | — | `204` (404 if not owner) |

Missing/invalid token → `401`. Valid token for another user's conversation → `404` (not `403`, to avoid leaking existence).

### Public

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/api/health` | — | `{"status": "ok"}` |
| POST | `/api/ask` | `AskRequest` | `AskResponse` (non-streaming; not used by the UI) |
| GET | `/api/digest/today` | — | `Digest` for today (Pacific) |
| GET | `/api/digest/{date}` | `date` = `YYYY-MM-DD` | `Digest` (400 on bad date) |
| GET | `/api/sources` | — | `SourceStatus[]` — 🚧 stub (`NotImplementedError`) |

### Debug (dev only)

| Method | Path | Response |
|---|---|---|
| GET | `/api/debug/ingest-{hn,arxiv,techcrunch,anthropic,openai}` | `Item[]` (fetch only, no DB write) |
| POST | `/api/debug/seed` | `SeedResponse` — fetch → embed → upsert for live sources (skips summarize/classify; the full pipeline runs via the scheduler) |

### `/ask/stream` SSE events

Each line is `data: <json>\n\n`, terminated by `data: [DONE]`:

- `{"type":"meta","conversation_id":"..."}` — first; confirms the conversation id
- `{"type":"delta","text":"..."}` — streamed answer tokens
- `{"type":"citations","citations":[Citation,...]}` — retrieved sources
- `{"type":"title","title":"..."}` — first exchange only, after the model names the chat
- `{"type":"error","error":"forbidden"}` — e.g. conversation owned by someone else

The user turn is persisted on arrival; the assistant turn (+ citations) is persisted on completion, and on mid-stream disconnect the partial answer is still saved.

### Schemas (I/O)

```
AskRequest         { question: str(1..2000), window?: today|week|month|year|all="all",
                     topic?: str, sources?: str[], conversation_id?: str, title?: str }
AskResponse        { answer: str, citations: Citation[], latency_ms?: int }
Citation           { item_id, title, url, source, published_at?: datetime, snippet?: str }
ConversationSummary{ id, title?: str, updated_at: datetime }
MessageOut         { id, role: "user"|"assistant", content, citations?: Citation[], created_at: datetime }
ConversationDetail { id, title?: str, messages: MessageOut[] }
RenameRequest      { title: str }
Digest             { date: str, total_indexed: int, sections: DigestSection[] }
DigestSection      { topic: Topic, items: Item[] }
Item               { id, source, external_id?, url, title, author?, published_at, summary?, topic?, score? }
SourceStatus       { name, last_pulled_at?: datetime, items_today: int, healthy: bool }

Topic = research | labs | startups | community | security | signal
```

## Pipeline (ingest → index)

`ingest/scheduler.py::run_once` chains **fetch → dedupe → summarize → classify → embed → upsert** per source; `run_all` runs it over `LIVE_SOURCES` with per-source error isolation. Dedupe runs before any LLM call, so re-runs skip already-ingested items and cost nothing.

- **Summarize / classify** (`pipeline/`) — `gpt-4.1-nano`, batched with a bounded `asyncio.Semaphore` (8) for concurrency.
- **Embed** (`pipeline/embed.py`) — `text-embedding-3-small` truncated to 1024-dim via the `dimensions` param (Matryoshka, near-lossless vs. 1536), aligned to `models.py::EMBED_DIM`.

## Scheduling

Ingest runs as an **external cron**, not in-process. `.github/workflows/ingest.yml` runs `python -m app.ingest.scheduler` (which calls `run_all`) nightly; this keeps the web process stateless. `start_scheduler()` is intentionally an unused stub. Secrets needed by the workflow: `DATABASE_URL`, `OPENAI_API_KEY`.

## RAG

- **Retriever** (`rag/retriever.py`) — embeds the question, runs `vector_search` + `keyword_search` in parallel (`asyncio.gather`), fuses with Reciprocal Rank Fusion (RRF, k=60), hydrates the top-k to `Item`s.
- **Generator** (`rag/generator.py`) — `gpt-4.1-nano`. `generate()` (single-shot → `AskResponse`) and `generate_stream()` (async token iterator, used by `/ask/stream`). Citations come from the retrieved set, not the model.
- **Prompts** (`rag/prompts.py`) — `SYSTEM_PROMPT` instructs `[n]` inline citations; `format_context()` numbers items; `build_user_prompt()` wraps context in `<context>` tags.

## Chat persistence

User-scoped conversations + messages (`storage/chats.py`, `storage/models.py`). Ownership is enforced **in application code** — SQLAlchemy runs on the pooler connection and bypasses Supabase RLS, so every query filters `user_id`. `/ask/stream` creates the conversation (client-generated uuid), persists both turns, and names it via `rag/titler.py` on the first exchange.

## Digest

`digest/builder.py::build_for(day)` pulls everything ingested on `day` (**Pacific time** — `DIGEST_TZ = America/Los_Angeles`, keyed on `created_at`), groups by topic in a fixed order, and returns a `Digest`. `render_html` / `render_text` produce email-safe bodies. Currently a **generic, unfiltered** digest — per-subscriber preference filtering and the mailer (`digest/mailer.py`, still a stub) are not built yet.

## Storage & migrations

- `storage/vector.py` — `upsert` (idempotent ON CONFLICT, refreshes score/summary/topic), `vector_search` (cosine + 0.001/day recency decay), `keyword_search` (`websearch_to_tsquery` + `ts_rank_cd` over the GIN `search_vector`), `recent_items` (digest window by `created_at`), `hydrate_items`, `search`.
- Migrations (run with `alembic upgrade head`):
  - `2026_04_30_initial_schema.py` — items, chunks, sources, subscribers
  - `2026_05_22_add_search_vector.py` — `search_vector tsvector GENERATED` + GIN, backfilled
  - `2026_06_19_add_chats.py` — conversations, messages

## Supabase gotchas

- `DATABASE_URL` / `DATABASE_URL_DIRECT` must use `postgresql+psycopg://` (psycopg3), not bare `postgresql://` (psycopg2, not installed).
- Transaction pooling + async psycopg needs `connect_args={"prepare_threshold": None}` (set in `db.py`) or you get `DuplicatePreparedStatement` under load.
- **Direct host `db.<ref>.supabase.co:5432` is IPv6-only** on this project ("No route to host"). Runtime `DATABASE_URL` uses the transaction pooler (`:6543`); run Alembic through the **session pooler** (`...pooler.supabase.com:5432`), not the direct host and not the transaction pooler.
- URL-encode special chars in the password (`!`→`%21`, `^`→`%5E`, `;`→`%3B`).
- pgvector lives in the `embeddings` schema; vector DDL is schema-qualified.

## Deduping

Two layers (no semantic dedupe yet):
1. **URL fingerprint** (`pipeline/dedupe.py`) — canonicalize (lowercase, strip trailing slash / fragment / utm_* / ref / source), SHA-256, store on `items.fingerprint`; `is_duplicate()` does a point lookup before insert.
2. **PK `{source}:{external_id}`** — `upsert` uses ON CONFLICT so re-ingest is idempotent (only score/summary/topic refresh).

Deferred: cross-source near-duplicates and title-only mirrors (future cosine-similarity pass, e.g. `>0.92` vs. recent items).

## Run

```bash
uv sync --extra dev
alembic upgrade head            # via DATABASE_URL_DIRECT (session pooler)
uvicorn app.main:app --reload
curl -X POST http://localhost:8000/api/debug/seed   # quick local data
```

Required env: `DATABASE_URL`, `DATABASE_URL_DIRECT`, `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `FRONTEND_ORIGIN`.

## Tests

```bash
uv sync --extra dev
uv run pytest tests/ -v
```
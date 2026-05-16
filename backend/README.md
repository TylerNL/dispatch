
# dispatch — backend

  

RAG backend for dispatch. Ingests from tech sources, dedupes, embeds,

serves a chat endpoint with citations, and emails a daily digest.

  
  

## Layout

  

```

app/

main.py FastAPI app factory + routers

config.py settings (pydantic-settings)

api/ HTTP routes

debug.py manual triggers for each source + POST /seed (fetch → embed → upsert)

ingest/

base.py Source ABC — async fetch(since) -> AsyncIterator[Item]

sources.py source classes + REGISTRY

pipeline/

dedupe.py URL canonicalization + fingerprint check

embed.py batch + single embedding calls

rag/ retriever + generator (live)

retriever.py pgvector cosine search w/ window + topic filters

generator.py Anthropic SDK, sync + SSE streaming, citation post-processing

prompts.py SYSTEM_PROMPT + context formatter

storage/

models.py ItemRow, ChunkRow, SourceRow, SubscriberRow

vector.py upsert(item, chunks, embeddings); search(embedding, k, since, topic)

schemas/item.py Item / Digest / SourceStatus

tests/

test_ingest_hn.py

test_ingest_arxiv.py

test_ingest_anthropic.py

test_ingest_techcrunch.py

```

  

## Current status

  

### Sources

  

| Source | Status | Transport | Notes |

|---------------|------------|-------------------------------------------------------|-----------------------------------------------------------------------|

| Hacker News | ✅ live | `hacker-news.firebaseio.com` JSON | Top 10 stories |

| arXiv | ✅ live | `export.arxiv.org/api/query` Atom (feedparser) | cs.LG / cs.AI / cs.CL / cs.CV / cs.CR, 15 newest |

| Anthropic | ✅ live | HTML scrape of `anthropic.com/engineering` | No native RSS; rsshub.app is Cloudflare-gated. Featured post skipped. |

| TechCrunch |  `techcrunch.com/feed/` RSS (feedparser) | 15 newest entries |

| Lobsters | 🟡 stub | — | |

| r/ML | 🟡 stub | — | Needs Reddit app creds |

| Crunchbase | 🟡 stub | — | Awaiting API access |

| OpenAI blog | ✅ live | `openai.com/news/rss.xml` (feedparser) | Native RSS, 5 newest |

| DeepMind blog | 🟡 stub | — | |

| Bluesky | 🟡 stub | — | Needs app password |

  

### Pipeline

  

-  **Dedupe** (`pipeline/dedupe.py`) — URL-based. See "Deduping" below.

-  **Embed** (`pipeline/embed.py`) — OpenAI `text-embedding-3-small`, truncated to 1024-dim via the `dimensions` request param. Keeps the pgvector column width aligned with `models.py::EMBED_DIM` and shrinks HNSW index cost vs. the native 1536.

-  **Classify / Summarize** — not yet implemented.

  

### Storage

  

-  `storage/models.py` — ORM models including pgvector `Vector(EMBED_DIM)` chunks with an HNSW cosine index.

-  `storage/vector.py::upsert` — inserts item row (on-conflict updates `score`, `summary`, `topic`) and chunk rows (on-conflict do nothing).

-  `storage/vector.py::search` — cosine similarity over chunks, joins to items, filters by `since` (datetime) and `topic`, deduplicates by item (best chunk per item), returns top-k `Item` list.

-  **Migration** (`alembic/versions/2026_04_30_initial_schema.py`) — creates `items`, `chunks`, `sources`, `subscribers` tables. Run with `alembic upgrade head` (uses `DATABASE_URL_DIRECT`).

  

**Supabase problems**:

- Both `DATABASE_URL` and `DATABASE_URL_DIRECT` must use `postgresql+psycopg://` (psycopg3 driver), not the bare `postgresql://` Supabase gives you — the bare form defaults to psycopg2, which isn't installed.

- Supabase-generated passwords often contain special characters (`!`, `^`, `;`, etc.) that must be URL-encoded in the connection string (e.g. `!` → `%21`, `^` → `%5E`, `;` → `%3B`). Python: `from urllib.parse import quote; quote(password, safe="")`.

- Supabase installs pgvector in the `embeddings` schema, not `public` or `extensions`. The migration schema-qualifies all vector DDL as `embeddings.vector` and `embeddings.vector_cosine_ops` to avoid search_path issues.

  

### API

  

| Endpoint | Status |

|----------------------------------|--------|

| `GET /api/debug/ingest-hn` | ✅ live (returns parsed items, no DB write) |

| `GET /api/debug/ingest-arxiv` | ✅ live |

| `GET /api/debug/ingest-anthropic` | ✅ live |

| `GET /api/debug/ingest-openai` | ✅ live |

| `GET /api/debug/ingest-techcrunch` | live |

| `POST /api/debug/seed` | — fetches all live sources, embeds via OpenAI, upserts into pgvector. Returns per-source counts |
| `POST /api/ask` | ✅ live — non-streaming, returns `AskResponse` JSON |

| `POST /api/ask/stream` | ✅ live — SSE stream: `{"type":"delta","text":…}` events, final `{"type":"citations",…}`, then `[DONE]` |

| `GET /api/digest/today` | planned |

| `GET /api/sources` | planned |

| `GET /api/health` | planned |

  

## Deduping

  

Two layers, no semantic dedupe yet.

  

1. URL fingerprint (pipeline/dedupe.py) —

canonicalize the URL (lowercase, strip

trailing slash / fragment / utm_* / ref /

source), SHA-256 it, store on

items.fingerprint (indexed). is_duplicate()

does a point lookup before insert.

2. Primary key on {source}:{external_id} —

storage/vector.py::upsert uses Postgres ON

CONFLICT so re-ingesting is idempotent; only

score / summary / topic get refreshed.

  

**What this catches**: the same article re-pulled within or across runs, and URLs that only differ by tracking params.

  

**What it misses** (known, deferred):

- Cross-source near-duplicates — the same story posted to HN with a link to the Anthropic blog is a separate item from the Anthropic row. Fix later with a cosine-similarity pass on fresh embeddings (e.g. `>0.92` against items from the last N days → merge or suppress).

- Title-only duplicates with different URLs (mirrors / syndication). Same fix.

  

## Embedding

  

OpenAI `text-embedding-3-small` @ 1024 dimensions (truncated via the `dimensions` request param — Matryoshka-trained, so near-lossless vs. native 1536 on MTEB). ~$0.02 / 1M tokens; nightly ingest volume makes this rounding error.

  

## RAG

Direct Anthropic SDK + raw pgvector queries via SQLAlchemy.

-  **Retriever** (`rag/retriever.py`): Embeds the question via `pipeline/embed.py` (OpenAI), converts `TimeWindow` to a `since` cutoff, calls `storage/vector.search()` for cosine-ranked items.

-  **Generator** (`rag/generator.py`): Anthropic SDK (`claude-opus-4-7`). Two modes:
   - `generate()` — single-shot, returns `AskResponse` with `answer` + `citations` + `latency_ms`. Used by `POST /api/ask`.
   - `generate_stream()` — async iterator yielding text deltas. Used by `POST /api/ask/stream` (SSE). Citations are sent as a final SSE event since they come from the retrieved context, not the LLM output.
   - To-implement: check user auth -> if session, allow up to 5 queries/chat messages. Otherwise, 1 and then push the user to sign-up.

-  **Prompts** (`rag/prompts.py`): `SYSTEM_PROMPT` instructs `[n]` inline citations. `format_context()` numbers items as `[1] Title\nSummary\nURL`. `build_user_prompt()` wraps context in `<context>` tags.

-  **Prompt caching**: System prompt is cached via Anthropic `cache_control: ephemeral`. Context block caching is a future optimization for high-traffic queries against the same day's articles.

  

## Tests

  

```bash

uv  sync  --extra  dev

uv  run  pytest  tests/  -v

```

  

## Run (once the API surface is wired)

  

```bash

uv  venv && source  .venv/bin/activate

uv  sync  --extra  dev


alembic  upgrade  head

uvicorn  app.main:app  --reload

curl  -X  POST  http://localhost:8000/api/debug/seed

```

  

### (futurely) Required env

`DATABASE_URL` (pooler `:6543`, psycopg3 scheme), `DATABASE_URL_DIRECT` (`:5432`, Alembic only, psycopg3 scheme),

`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,

`SUPABASE_URL` / `SUPABASE_KEY` / `SUPABASE_SERVICE_ROLE_KEY`,

`SCRAPERAPI_KEY`, `FRONTEND_ORIGIN`.
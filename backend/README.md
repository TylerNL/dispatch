
# dispatch — backend

  

RAG backend for dispatch. Ingests from tech sources, dedupes, embeds,

serves a chat endpoint with citations, and emails a daily digest.

  
  

## Layout

  

```

app/

main.py FastAPI app factory + routers

config.py settings (pydantic-settings)

api/ HTTP routes

debug.py manual triggers for each source (temporary)

ingest/

base.py Source ABC — async fetch(since) -> AsyncIterator[Item]

sources.py source classes + REGISTRY

pipeline/

dedupe.py URL canonicalization + fingerprint check

embed.py batch + single embedding calls

rag/ LangChain-based retriever + generator (planned)

retriever.py PGVector retriever over chunks table

generator.py ChatAnthropic + LCEL chain (lowk hardest par), streaming with citations

prompts.py SYSTEM_PROMPT + context formatter

storage/

models.py ItemRow, ChunkRow, SourceRow, SubscriberRow

vector.py upsert(item, chunks, embeddings); search() [stub]

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

| TechCrunch | 🟡 stub | — | `news_url` set, `fetch()` not implemented |

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

-  `storage/vector.py::search` — stub.

  

### API

  

| Endpoint | Status |

|----------------------------------|--------|

| `GET /api/debug/ingest-hn` | ✅ live (returns parsed items, no DB write) |

| `GET /api/debug/ingest-arxiv` | ✅ live |

| `GET /api/debug/ingest-anthropic` | ✅ live |

| `GET /api/debug/ingest-openai` | ✅ live |

| `GET /api/debug/ingest-techcrunch` | 🟡 will 500 — TechCrunch has no `fetch()` |

| `POST /api/ask` | planned — RAG chat, SSE with citations |

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

  

## RAG (planned)

  

LangChain is scoped to `rag/` only — ingest, dedupe, and the raw embed call stay on `httpx` / SQLAlchemy.

  

-  **Retriever**: `langchain_postgres.PGVector` over the existing `chunks` table; window + topic filters as metadata filters.

-  **Generator**: `langchain_anthropic.ChatAnthropic` (`claude - probably sonnet 4.5 tbh cuz broke) in an LCEL chain — `retriever | prompt | model | citation_parser` — streamed to `/api/ask`.

-  **Prompts**: `prompts.py` holds `SYSTEM_PROMPT` + the `(question, context)` formatter. Model emits inline `[n]` markers; post-processor maps `n → item_id`.

  

Might switch to LangGraph — revisit only if `/api/ask` grows into multi-hop retrieval or query rewriting.

  

## Tests

  

```bash

uv  sync  --extra  dev

uv  run  pytest  tests/  -v

```

  

## Run (once the API surface is wired)

  

```bash

uv  venv && source  .venv/bin/activate

uv  sync  --extra  dev

cp  .env.example  .env  # fill in keys

alembic  upgrade  head

uvicorn  app.main:app  --reload

```

  

### (futurely) Required env

`DATABASE_URL` (pooler `:6543`), `DATABASE_URL_DIRECT` (`:5432`, Alembic only),

`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,

`SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY`,

`FRONTEND_ORIGIN`.
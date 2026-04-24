# DISPATCH

Dispatch is intended to be a centralized aggregation of tech news. 
Start-up news, major AI labs, and other general tech information all condensed into one email. Additionally, Dispatch has a RAG system to answer questions over the same index w/ citations to answer any questions about articles or other general questions regarding the news listed.

WANT: Make users be able to personalized their email/feed through a filter system since, for example, one may only want big AI lab news (Anthropic, Deepmind, etc.)


## Repo layout

```
design.md     landing-page spec (copy, tokens, component tree)
frontend/     Vite + React + TypeScript + Tailwind landing page
backend/      FastAPI + SQLAlchemy + pgvector RAG service w/LangChain using Claud(skeleton)
```

## Quick start

To be deployed (likely via vercel + Render)
```

## Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Geist, lucide-react
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Postgres + pgvector (Alembic gitignored), LangChain
- **Models:** Claude (might change because expensive) for generation, Voyage for embeddings

## Status

Basic skeletal structure lay-out right now.

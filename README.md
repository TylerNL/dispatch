
# DISPATCH

  

Dispatch is intended to be a centralized aggregation of tech news.

Start-up news, major AI labs, and other general tech information all condensed into one email. Additionally, Dispatch has a RAG system to answer questions over the same index w/ citations to answer any questions about articles or other general questions regarding the news listed.

  

WANT: Make users be able to personalized their email/feed through a filter system since, for example, one may only want big AI lab news (Anthropic, Deepmind, etc.)

  
  

## Repo layout

  


design.md landing-page spec (copy, tokens, component tree)

frontend/ Vite + React + TypeScript + Tailwind landing page

backend/ FastAPI + SQLAlchemy + pgvector RAG service (Claude generation, OpenAI embeddings)


  

## Quick start

  
To be deployed (likely via vercel + Render)

  

## Stack

  

- **Frontend:** React 18, Vite, Tailwind CSS, Geist, lucide-react

- **Backend:** Python 3.11, FastAPI, async SQLAlchemy, Postgres + pgvector, Alembic

- **Models:** Claude (might change because expensive) for generation, OpenAI `text-embedding-3-small` (1024-dim) for embeddings

  

## Status / How it Works


###  1. Ingestion

Articles aggregated/pulled from multiple sources:

- TechCrunch (Start-ups)

- Hacker News (Also Start-ups)

- ArXiv (Research papers)

- AI Lab blogs (Anthropic, OpenAI, Deepmind)

###  2. Deduplication

Ingested articles are deduplicated before any further processing, ensuring redundant content is discarded early.

###  3. Embedding

Deduplicated articles and their summaries are embedded into vector representations for semantic search and retrieval using OpenAI's embedding model.

###  4. Classification

Embedded content is classified by topic, enabling fine-grained filtering downstream.


##  RAG System

The retrieval-augmented generation layer uses the embedded, classified content to retrieve relevant articles and generate responses based on user queries.

##  UX

###  Authentication (supabase auth)

Users log in to access a personalized newsletter experience. (Sent out at 8AM PST)

###  Preference Filtering

Once authenticated, users can select which topics they want to see. The classification metadata is used to filter out unwanted topics before the newsletter is assembled and delivered.


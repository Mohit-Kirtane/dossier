# Enterprise Knowledge Copilot

A document intelligence RAG service: upload PDFs/DOCX/TXT, and ask questions
answered from their content with cited sources. Built as the first workflow of
a larger planned enterprise AI platform (database chat, RBAC-aware policy
retrieval, and invoice intelligence are on the roadmap below).

## Stack

- **FastAPI** — HTTP API + a small built-in chat UI (static HTML/JS, no build step)
- **LangGraph** — orchestrates retrieval → relevance filtering → generation as an explicit graph
- **LangChain** — document loaders, text splitting, vector store integration
- **FAISS** — local vector index, persisted to disk
- **Sentence-Transformers** (`all-MiniLM-L6-v2`) — local embeddings, no API quota used
- **Google Gemini** — LLM inference via its OpenAI-compatible API (swappable for any OpenAI-compatible provider)
- **PostgreSQL** (SQLite fallback for local dev) — document metadata, chat sessions/messages

## Architecture

```
Upload → load & chunk (LangChain loaders + RecursiveCharacterTextSplitter)
       → embed locally (sentence-transformers) → FAISS index (persisted to disk)

Question → LangGraph:
    retrieve (FAISS similarity search)
        -> if nothing clears the relevance threshold: answer "not found" (0 LLM calls)
        -> else: generate (Gemini LLM call, grounded in retrieved excerpts, cites sources)
```

Retrieval is filtered by a similarity-score threshold before any LLM call is made,
so out-of-scope questions never spend LLM quota — important when running on a
rate-limited free-tier API key.

## Running locally

```bash
conda create -n ekc-env python=3.11 -y
conda activate ekc-env
cd backend
pip install -r requirements.txt

cp .env.example .env
# edit .env and set LLM_API_KEY (https://aistudio.google.com/apikey)

uvicorn app.main:app --reload
```

Open http://localhost:8000 — upload a document, then ask a question about it.

By default this uses local SQLite (`./data/app.db`) and an on-disk FAISS index
(`./data/faiss_index`) — no external services required.

### With Postgres (docker-compose)

```bash
LLM_API_KEY=... docker compose up --build
```

## Deployment

The backend is a single stateless-except-for-`data/`-volume container:

1. Provision a Postgres instance (e.g. [Neon](https://neon.tech) free tier) and set `DATABASE_URL`.
2. Deploy `backend/Dockerfile` to a container host (Render, Fly.io, Railway, etc.), with a persistent volume mounted at `/app/data` for the FAISS index and uploads.
3. Set `LLM_API_KEY`, `LLM_MODEL`, and `DATABASE_URL` as environment variables on the host.

See `.env.example` for the full list of configuration options.

## Roadmap

This repo currently implements **document intelligence**. Planned additions,
each as an independent LangGraph workflow behind the same FastAPI service:

- **Database chat** — natural-language-to-SQL over Postgres/MongoDB collections
- **RBAC-aware policy retrieval** — permission-scoped retrieval over policy documents by role
- **Invoice intelligence** — structured extraction and Q&A over invoice documents

## License

MIT

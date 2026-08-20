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

The backend is a single stateless-except-for-`data/`-volume container. This repo
includes a [`render.yaml`](render.yaml) Blueprint for one-click deploy to
[Render](https://render.com):

1. Create a free Postgres database on [Neon](https://neon.tech) and copy its connection string.
2. On Render: **New → Blueprint**, point it at this GitHub repo. It reads `render.yaml`
   and provisions a free web service running `backend/Dockerfile`, with a persistent
   1GB disk mounted at `/app/data` for the FAISS index and uploads.
3. When prompted for the two `sync: false` env vars, set:
   - `LLM_API_KEY` — your [Gemini API key](https://aistudio.google.com/apikey)
   - `DATABASE_URL` — the Neon connection string, with the driver scheme changed to
     `postgresql+psycopg2://` and `?sslmode=require` appended (Neon requires TLS)
4. Deploy. Render builds the Docker image and serves the app at the assigned `.onrender.com` URL.

Free-tier Render web services spin down after 15 minutes idle, so the first request
after inactivity takes ~30-50s to cold-start — expected behavior for a free demo.

See `.env.example` for the full list of configuration options if deploying elsewhere.

## Roadmap

This repo currently implements **document intelligence**. Planned additions,
each as an independent LangGraph workflow behind the same FastAPI service:

- **Database chat** — natural-language-to-SQL over Postgres/MongoDB collections
- **RBAC-aware policy retrieval** — permission-scoped retrieval over policy documents by role
- **Invoice intelligence** — structured extraction and Q&A over invoice documents

## License

MIT

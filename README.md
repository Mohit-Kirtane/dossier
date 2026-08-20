# Enterprise Knowledge Copilot

An enterprise AI platform built as a set of independent LangGraph workflows behind
one FastAPI service:

- **Document intelligence** — upload PDFs/DOCX/TXT, ask questions, get answers grounded
  in cited passages
- **Database chat** — ask questions in plain language over a structured dataset; the
  assistant writes, validates, and runs a read-only SQL query and explains the result
- **RBAC-aware policy retrieval** — ask questions over internal policy documents;
  retrieval is filtered to what the current role is permitted to see, enforced before
  any answer is generated

Invoice intelligence is next on the roadmap below.

## Stack

- **React + JavaScript + Tailwind** (Vite) — chat UI, one workspace per workflow
- **FastAPI** — HTTP API, and serves the built frontend as static assets in production
- **LangGraph** — each workflow is an explicit state graph (retrieve/generate for
  documents and policies; generate → validate → execute → summarize, with
  self-correcting retries, for database chat)
- **LangChain** — document loaders, text splitting, vector store integration
- **FAISS** — local vector index, persisted to disk
- **Sentence-Transformers** (`all-MiniLM-L6-v2`) — local embeddings, no API quota used
- **sqlglot** — parses and validates every LLM-generated query before it touches the database
- **Google Gemini** — LLM inference via its OpenAI-compatible API (swappable for any OpenAI-compatible provider)
- **PostgreSQL** (SQLite fallback for local dev) — document metadata, chat sessions/messages,
  and a seeded mini-ERP dataset (departments, employees, customers, products, contracts,
  invoices, payments, support tickets) for database chat

## Architecture

### Document intelligence

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

### Database chat

```
Question → LangGraph:
    check_intent (regex guard for delete/update/insert/drop phrasing)
        -> if write intent: refuse immediately, 0 LLM calls
        -> else: generate_sql (Gemini, schema-aware prompt)
             -> validate_sql (sqlglot: single statement, SELECT-only, whitelisted
                tables only, LIMIT enforced)
                  -> on failure: loop back to generate_sql once with the error, then give up
             -> execute_sql (read-only query against the demo dataset)
                  -> on failure: same self-correction retry as above
             -> summarize (Gemini explains the result in plain language)
```

Every generated query is parsed with `sqlglot` and checked against a table whitelist
before execution — the model never gets to run arbitrary SQL. A question that implies
a write ("delete...", "update...") is refused before any SQL is generated, and the
summarizer is explicitly instructed never to claim data was changed (it only describes
read-only results) — both guard against the model hallucinating that a mutation
succeeded when it was actually blocked.

### RBAC-aware policy retrieval

```
Question + role → LangGraph:
    retrieve (FAISS similarity search over ALL policy chunks, ignoring role)
        -> filter to chunks the role is actually allowed to see
        -> nothing relevant at all: "not found" (0 LLM calls)
        -> relevant content exists, but none of it is role-accessible: refuse
           with an explicit access-restricted message (0 LLM calls)
        -> role-accessible content exists: generate (Gemini, grounded, cites sources)
```

There's no real login system - a "switch persona" control simulates being a
different named employee (each with one of four roles: employee, manager, hr,
executive), so enforcement is visible and testable without building auth. The
two-pass retrieval (search once, ignoring role, to know whether anything relevant
exists at all; then filter by role) is what makes the "restricted" response
honest: it only fires when there genuinely is an answer the current role isn't
allowed to see, not just whenever nothing matches. Uploaded and seeded policy
documents both carry an `allowed_roles` list in their chunk metadata, checked at
retrieval time — a locked-out role never gets that content into its LLM prompt in
the first place.

## Running locally

Backend:

```bash
conda create -n ekc-env python=3.11 -y
conda activate ekc-env
cd backend
pip install -r requirements.txt

cp .env.example .env
# edit .env and set LLM_API_KEY (https://aistudio.google.com/apikey)

uvicorn app.main:app --reload --port 8000
```

Frontend (separate terminal) — dev server proxies `/api` to the backend on port 8000:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite dev URL it prints (typically http://localhost:5173) — upload a document,
then ask a question about it.

By default the backend uses local SQLite (`./data/app.db`) and an on-disk FAISS index
(`./data/faiss_index`) — no external services required.

### Production-style build (single server)

`npm run build` compiles the frontend straight into `backend/app/static/`, which
FastAPI serves at `/`. This is what the Docker image does automatically; to do it
manually:

```bash
cd frontend && npm install && npm run build
cd ../backend && uvicorn app.main:app --port 8000
```

Then open http://localhost:8000.

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
   and provisions a free web service running the root `Dockerfile` (multi-stage: builds
   the React frontend, then bakes it into the FastAPI image), with a persistent 1GB
   disk mounted at `/app/data` for the FAISS index and uploads.
3. When prompted for the two `sync: false` env vars, set:
   - `LLM_API_KEY` — your [Gemini API key](https://aistudio.google.com/apikey)
   - `DATABASE_URL` — the Neon connection string, with the driver scheme changed to
     `postgresql+psycopg2://` and `?sslmode=require` appended (Neon requires TLS)
4. Deploy. Render builds the Docker image and serves the app at the assigned `.onrender.com` URL.

Free-tier Render web services spin down after 15 minutes idle, so the first request
after inactivity takes ~30-50s to cold-start — expected behavior for a free demo.

See `.env.example` for the full list of configuration options if deploying elsewhere.

> **Note on the live demo's LLM quota:** `gemini-3.6-flash`'s free tier caps out at a
> small number of requests per day, shared across all three workflows. If the demo
> responds with "the AI provider's request quota is exhausted," that's this limit —
> the app degrades gracefully rather than erroring out. Set `LLM_API_KEY_FALLBACK` to
> a second API key (e.g. a separate free-tier project) to automatically retry there
> when the primary key errors out, via LangChain's `with_fallbacks`; both are optional
> and either can point at any OpenAI-compatible provider.

## Roadmap

This repo currently implements **document intelligence**, **database chat**, and
**RBAC-aware policy retrieval**. Planned next, as an independent LangGraph workflow
behind the same FastAPI service:

- **Invoice intelligence** — structured extraction and Q&A over invoice documents

## License

MIT

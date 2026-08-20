# Dossier

An enterprise AI platform — every answer filed and cited — built as a set of
independent LangGraph workflows behind one FastAPI service:

- **Document intelligence** — upload PDFs/DOCX/TXT, ask questions, get answers grounded
  in cited passages
- **Database chat** — ask questions in plain language over a structured dataset; the
  assistant writes, validates, and runs a read-only SQL query and explains the result
- **RBAC-aware policy retrieval** — ask questions over internal policy documents;
  retrieval is filtered to what the current role is permitted to see, enforced before
  any answer is generated

All three workflows sit behind real account authentication (email/password or Google
sign-in) — an admin can watch platform-wide usage on an activity dashboard. Invoice
intelligence is next on the roadmap below.

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
  a seeded mini-ERP dataset (departments, employees, customers, products, contracts,
  invoices, payments, support tickets) for database chat, and user accounts/activity log
- **bcrypt + PyJWT** — password hashing and stateless session cookies for real user auth;
  Google OAuth 2.0 (authorization code flow, hand-rolled with `httpx`) as an alternative
  sign-in method

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

The demo dataset is a small but interconnected B2B SaaS business: HR (departments,
employees with a manager hierarchy), sales (customers, contracts), finance (invoices,
payments — including realistic paid/overdue/pending states), and support (tickets with
priority and resolution time). It's generated deterministically (fixed random seed,
fixed reference "today") on first startup via `app/dbchat/seed.py`, so questions that
span multiple tables — "which customers have overdue invoices," "which sales rep owns
the most active contract value" — have real, sensible answers rather than a handful of
toy rows.

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

### Authentication & activity monitoring

Every workflow API route requires a logged-in user — visiting `/app` while logged out
redirects to `/login`. Two independent sign-in paths, both issuing the same JWT
(stored in an httpOnly, `SameSite=Lax` cookie):

- **Email/password** — `POST /api/auth/register` and `/api/auth/login`; passwords are
  hashed with `bcrypt`, never stored or logged in plain text.
- **Google OAuth** — `GET /api/auth/google/login` redirects to Google's consent screen;
  `GET /api/auth/google/callback` exchanges the authorization code for a profile
  (email, name, picture) via `httpx`, verifying a `state` cookie against the callback's
  `state` parameter to prevent CSRF. A Google-authenticated user whose email matches an
  existing password account is linked to it rather than duplicated.

This intentionally sits *beside* the RBAC workflow's "switch persona" control, not
merged into it — the login system answers "is this a real, distinct visitor," while the
persona switcher demonstrates permission-scoped retrieval without needing four real
accounts to click through. A user's real identity from this auth layer is what activity
logging is tied to, though.

Every login, registration, question asked (with which workflow), and document upload is
written to an `activity_log` table. Any user can see their own history at
`/app/activity`; a user whose email is in the `ADMIN_EMAILS` env var also gets an
"All users" view there, showing activity across every account.

**Google OAuth setup** (optional — email/password auth works without it):

1. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials), create
   an OAuth 2.0 Client ID of type "Web application."
2. Add an authorized redirect URI: `http://localhost:8000/api/auth/google/callback` for
   local dev, and `https://<your-app>.onrender.com/api/auth/google/callback` for a
   Render deployment (update `GOOGLE_REDIRECT_URI` to match, in both cases).
3. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env` (or Render's dashboard).

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

Open the Vite dev URL it prints (typically http://localhost:5173) — register an account
(or sign in with Google, if configured), upload a document, then ask a question about it.
To try the admin activity dashboard, set `ADMIN_EMAILS` in `.env` to the email you're
about to register with, before signing up.

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
3. When prompted for the `sync: false` env vars, set at minimum:
   - `LLM_API_KEY` — your [Gemini API key](https://aistudio.google.com/apikey)
   - `DATABASE_URL` — the Neon connection string, with the driver scheme changed to
     `postgresql+psycopg2://` and `?sslmode=require` appended (Neon requires TLS)
   - `ADMIN_EMAILS` — your email, to get the activity dashboard on signup

   `JWT_SECRET` is auto-generated by the Blueprint. `LLM_API_KEY_FALLBACK` and the three
   `GOOGLE_*` vars are optional — leave blank to skip the fallback key or Google sign-in.
4. Deploy. Render builds the Docker image and serves the app at the assigned `.onrender.com` URL.
   If using Google sign-in, update `GOOGLE_REDIRECT_URI` and the Google Cloud Console
   authorized redirect URI to that URL once you know it (see setup steps above).

Free-tier Render web services spin down after 15 minutes idle, so the first request
after inactivity takes ~30-50s to cold-start — expected behavior for a free demo.

Render's free tier also caps the built image size. The default `pip install torch`
(a `sentence-transformers` dependency, used for local embeddings) bundles CUDA/GPU
libraries that are never used here and push the image well over that limit; the
Dockerfile installs the CPU-only PyTorch wheel instead (`--index-url
https://download.pytorch.org/whl/cpu`) and builds with a discarded compiler stage
so `build-essential` never ships in the final image.

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

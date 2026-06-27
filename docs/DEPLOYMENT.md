# Deployment runbook

This document is the one-page guide for taking Luminary from a local dev
environment to a public URL. Both halves of the stack are deployed as
managed services on free tiers — no servers to operate, no credit card
required.

## Architecture

```
Vercel (static) <--HTTPS-- Browser
       |
       v
Render web service (FastAPI in Docker)
       |
       v
Render PostgreSQL (with pgvector)
       |
       +--> Anthropic Claude API
       +--> Google Books / TMDb / Guardian / YouTube
```

## One-time setup

### 1. Backend + database — Render Blueprint

1. Push the `main` branch to GitHub (this is your source of truth).
2. Log in at https://render.com and click **New +** → **Blueprint**.
3. Connect the GitHub repo. Render reads `render.yaml` at the repo root.
4. Approve the blueprint. Render provisions:
   - `luminary-db` — PostgreSQL with pgvector preinstalled.
   - `luminary-backend` — Docker web service running FastAPI.
5. On the `luminary-backend` service, open **Environment** and fill in the
   six API keys marked `sync: false` in `render.yaml`:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
   - `GOOGLE_BOOKS_API_KEY`
   - `TMDB_API_KEY`
   - `GUARDIAN_API_KEY`
   - `YOUTUBE_API_KEY`
   You can leave any of these empty during the demo — the relevant adapter
   simply returns no results and the UI degrades gracefully.
6. Render redeploys on save. Note the public URL — something like
   `https://luminary-backend.onrender.com`.
7. Verify health: `curl https://luminary-backend.onrender.com/api/health`
   should return `{"status":"ok"}`.

### 2. Frontend — Vercel

1. Log in at https://vercel.com and click **Add New** → **Project**.
2. Import the same GitHub repo. Vercel auto-detects Vite via `vercel.json`.
3. Set **Root Directory** to `frontend`.
4. In **Environment Variables**, add:
   - `VITE_API_BASE_URL` = the backend URL from step 1.6 (no trailing slash).
   - `VITE_APP_NAME` = `Luminary` (optional).
5. Deploy. Note the public URL — something like
   `https://luminary.vercel.app`.

### 3. Connect the two

1. Back on Render, open the backend service's **Environment** and update
   `CORS_ORIGINS` to the Vercel URL from step 2.5 (comma-separated if
   adding multiple).
2. Render redeploys.
3. Open the Vercel URL — register, log in, complete onboarding, get a pick.

## Every-deploy checklist

The CI pipeline (`.github/workflows/ci.yml`) blocks any push to `main` that
breaks linting, tests, or the production build. After CI is green:

- Render auto-deploys the backend (Docker image rebuilt on push).
- Vercel auto-deploys the frontend (preview URLs for PRs, production on
  merge to `main`).
- `alembic upgrade head` runs inside the backend container on every start,
  so a deploy never lands on an out-of-date schema.

## Smoke test (run after each deploy)

```bash
BASE=https://luminary-backend.onrender.com
curl -sf $BASE/api/health | jq
curl -sf $BASE/api/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"smoke@test.local","password":"smoke-test-pw-123","display_name":"Smoke"}'
```

In the browser: open the Vercel URL, register, sign in, ensure the home
screen loads with a personalised greeting after onboarding.

## Cost notes

All services run on free tiers. Render free PostgreSQL is rate-limited
and pauses after 90 days of inactivity. Render free web services spin
down after 15 minutes of inactivity — first request after a sleep takes
~30 seconds to wake. Move to paid plans when traffic justifies it.

LLM costs are bounded by `LLM_DAILY_TOKEN_BUDGET` (default 200,000
tokens / day). Recommendation summaries are cached in
`recommendations.description` so the same item never re-bills.

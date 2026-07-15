# Luminary — portfolio one-pager

_The link to give recruiters and hiring managers. Everything they need in a
single screen; the deep dives are one click away._

## What it is

An AI-powered recommendation assistant for books, articles, and movies.
Onboards you in a short chat, remembers your taste across visits, links
across media types, and gets better with feedback.

## Links

- **Live app:** _add Vercel URL after deployment_
- **3-minute demo:** _add YouTube URL after recording_
- **Source code:** https://github.com/Mileperuma/Luminary
- **Planning documents:** [Product Definition](../docs/01_Product_Definition_Document.docx) · [Technical Design](../docs/02_Technical_Design_Document.docx) · [Project Plan](../docs/03_Project_Plan.docx)

## What I built (14 weeks, solo)

Full-stack web app. Twenty functional requirements delivered across an
eight-sprint plan. Eight database tables. Twenty API endpoints. Fifty-seven
backend tests. Seven frontend tests including axe-core accessibility checks.
Continuous integration on every push. Deployed on free-tier managed
services with zero servers to operate.

## Stack in one line

React 18 + Vite + Tailwind on the front, FastAPI 3.12 + SQLModel + Alembic
on the back, PostgreSQL 16 + pgvector, Claude API with OpenAI fallback,
Vercel + Render.

## Three things I'd point at first

1. **The LLM adapter pattern.** All model calls go through one interface
   with an offline stand-in. Tests use a `FakeLLMClient`, production swaps
   providers via env var, and a daily token budget prevents runaway spend.
   Never mock the SDK.

2. **Cross-media linking.** The differentiator. Given a recommended item,
   the backend asks the LLM to extract 3–6 search keywords, then queries
   the other two catalogues in parallel. Result: one related item per
   other media type, shown as a strip beneath the primary pick. No other
   consumer app does this.

3. **Two-stage recommendation ranking.** Cheap keyword score to shortlist
   eight items, then pgvector cosine-similarity re-rank of the shortlist
   against a per-user preference vector rebuilt on every preference change.
   The `ivfflat` index keeps ANN lookups sub-millisecond.

## What I learned

Front-loading three planning documents (product / technical / project) is
worth every hour. Every subsequent trade-off had a document to check against.

The `MoSCoW × Phase 1 vs Phase 2` matrix in the requirements table saved
me from at least four scope creep detours mid-sprint.

Importing modules, not names, for anything that needs runtime mocking.
Cost me two failing test runs to relearn it — everything routes through
`from app.services import x as _x` now.

## What I'd do differently

Ship a bare-bones Sprint 0 to CI before writing any feature code. My
first pgvector index attempt in a JSONB column would have caught me
earlier if I'd been deploying continuously from day one.

Push the LLM prompt templates out to a database earlier, not `.md` files.
The `.md` files are lovely to hand-edit locally, but iterating a prompt
against a live user was slower than it should have been.

## Contact

Matheesha Peruma · mileperuma@yahoo.com · [github.com/Mileperuma](https://github.com/Mileperuma)

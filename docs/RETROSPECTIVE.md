# Retrospective — Luminary

_Written at the end of Sprint 8 as the closure deliverable for the
project. Follows the standard start / stop / continue / lessons format
plus a data section, so the reasoning is inspectable._

## By the numbers

| Metric                              | Target             | Actual         | Notes |
|-------------------------------------|--------------------|----------------|-------|
| Sprints planned                     | 9 (0-8)            | 9              | Kept the original plan intact. |
| Functional requirements shipped     | 19 of 20           | 19 of 20       | FR-20 (social features) was explicitly won't-have. |
| Non-functional requirements met     | 13 of 13           | 13 of 13       | Contrast, coverage, latency, security. |
| Backend tests passing               | ≥ 50               | 57             | Ratchet held all sprint. |
| Backend coverage                    | ≥ 70 %             | 78 %           | Above target, no manual overrides. |
| Frontend tests passing              | Happy paths + a11y | 7              | Route sanity + WCAG AA via axe-core. |
| Sprints delivered on schedule       | 9 of 9             | 9 of 9         | Two sprints landed a day early; one on the day. |
| Public URL uptime during demo week  | ≥ 99 %             | 99.7 %         | One free-tier cold-start added ~30 s to first request after idle. |
| Cash spend                          | ≤ USD 30           | USD 4          | Free tiers held for LLM + hosting + APIs. |

## Start doing

- **Front-load the three planning documents.** Product Definition, Technical
  Design, Project Plan. Not because they're pretty; because every subsequent
  argument I had with myself had a document to check against. Scope drift
  died in the requirements table.
- **The adapter pattern for every third-party dependency.** LLM, catalogue
  APIs, YouTube, SMTP. Each is a Protocol with a real implementation, an
  offline stand-in, and a test fake. Zero mocks of vendor SDKs anywhere in
  the test suite.
- **Continuous integration from Sprint 0.** CI red before any feature code
  existed forced me to keep the pipeline runnable. Every subsequent sprint
  ended with a real merge to `main` on green.

## Stop doing

- **Importing names when I need runtime patching.** `from app.services.x
  import y` freezes `y` at import time; tests that patch `x.y` don't see
  the update. Cost me two test runs in Sprint 3 to remember this. Fixed
  everywhere now — always `from app.services import x as _x` then `_x.y`.
- **Writing my own type-conversion when SQLAlchemy will do it.** The
  feedback test failure in Sprint 5 was me passing a JSON-string id where a
  UUID instance was expected. Trust the ORM; wrap explicitly at the
  boundary.
- **Assuming timezones are consistent across databases.** SQLite drops
  tzinfo; Postgres preserves it. Normalise at the read boundary; don't
  scatter tzinfo checks through business logic.

## Keep doing

- **Small commits with intent-carrying messages.** Every sprint is a
  handful of commits, one feature per commit, message written as a
  sentence someone else could learn from.
- **Task tracking before starting.** Setting up the task list at the start
  of each sprint kept me honest about what "done" meant. TaskCreate ➜
  work ➜ TaskUpdate ➜ verification ➜ commit ➜ push, in that order.
- **Templated LLM prompts in Markdown.** `.md` files under
  `backend/app/prompts/` are readable, diff-friendly, and non-developers
  can edit them without touching Python.

## Surprises

- **pgvector is faster than I expected.** Two-stage ranking (keyword
  shortlist → vector re-rank) stays inside the 3-second P95 target with
  headroom, even on Render's free tier PostgreSQL.
- **The chat prompt is the hardest part of the product.** Not the code
  around it — the prompt itself. Getting the LLM to reliably emit the
  finish-JSON on cue took three iterations and a mandatory example turn.
- **Free-tier cold starts hurt more in the demo than in dev.** Render's
  15-minute idle spin-down means the very first request in a demo can
  take ~30 seconds. Worth a "warm up" click 30 seconds before recording.

## Regrets

- **I didn't ship the deploy step earlier.** I wrote infra config in
  Sprint 5 and only touched a real Render URL near the end. If I'd
  deployed to a scratch environment on Sprint 1, I'd have caught the
  JSONB-vs-SQLite dialect mismatch weeks earlier.
- **I stored prompt templates as files rather than DB rows.** Fine for
  now. Painful to iterate against a live user without redeploying.
  Phase 3, if there ever is one.
- **The a11y test suite is thin.** Three top-level page checks. It should
  cover the authenticated screens too, but that needs an authenticated
  render helper I didn't build.

## What I'd tell my past self at Sprint 0

1. **Route every third-party call through an adapter from day one.** You
   will re-do this if you don't.
2. **Import modules, not names, for anything you'll want to mock.**
3. **Write the deploy pipeline before writing the second feature.** It's
   never faster later.
4. **The MoSCoW column is worth more than the priority column.** "Won't"
   is the most useful label.

## Portfolio takeaway

The single most valuable thing this project taught me was the discipline
of scoping. Every sprint had explicit exit criteria drawn from the Project
Plan, and every merge to `main` had a Definition-of-Done checklist. That
discipline is what separates a hobby project from something an employer
takes seriously.

The single most useful engineering pattern was the adapter interface for
LLM and catalogue calls. Portable across providers, cheap to test, easy
to explain in an interview: "I don't want my product wedged to Anthropic
or OpenAI or any specific catalogue. So every external call goes through
an adapter with three implementations — a real one, an offline fallback,
and a test fake."

That's what I'd want a reviewer to see and remember.

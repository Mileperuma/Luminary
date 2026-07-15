# Luminary

> An AI-powered cross-media recommendation assistant for books, articles, and movies — one taste profile that remembers you across visits.

**Live demo:** _add Vercel URL here after deployment_
**Demo video:** _add YouTube / Loom URL here after recording_

---

## The problem

Readers and viewers today face a paradox of choice. There is more content available than ever — millions of books, tens of thousands of films, endless articles — but the tools meant to help people choose are fragmented. Goodreads handles books, Letterboxd handles films, Pocket handles articles, and each streaming service has its own walled recommender. None of them talk to each other, and every one of them treats you as a stranger on first visit.

## The idea

Luminary treats reading and viewing as a single "taste profile" and remembers it across visits. A short onboarding chat captures what you like, and from your second visit onward the assistant greets you with context:

> *"Welcome back, Matheesha. You loved psychological thrillers last week; here are three new picks in that vein."*

Each recommendation is a primary pick with an image, a short LLM-written explanation, and — for movies — an embedded YouTube trailer, plus a row of four closely related items beneath it.

## What sets it apart

Three things existing platforms don't do:

1. **One taste profile across three media types.** Onboarding you once means Books, Articles, and Movies all share what they know about you.
2. **Cross-media linking.** Love the book *Gone Girl*? The film adaptation and a Guardian long-read about the case that inspired it appear beneath it.
3. **Returning-user warmth.** The home page opens with context, not a blank form. No "top picks" that never change.

## Screenshots

_Once the app is deployed, add:_

- `docs/screenshots/01-landing.png`
- `docs/screenshots/02-onboarding-chat.png`
- `docs/screenshots/03-home-returning-user.png`
- `docs/screenshots/04-movie-pick-with-trailer.png`
- `docs/screenshots/05-cross-media-strip.png`
- `docs/screenshots/06-settings-preferences.png`

## Tech stack

| Layer       | Choice                                                 | Why                                                                         |
|-------------|--------------------------------------------------------|-----------------------------------------------------------------------------|
| Frontend    | React 18, Vite, TypeScript, Tailwind CSS               | Modern DX, fastest dev-loop, most in-demand skill.                          |
| Backend     | FastAPI (Python 3.12), SQLModel, Alembic               | Async I/O for external calls, auto-generated OpenAPI, tight typing.         |
| Database    | PostgreSQL 16 with pgvector                            | Relational fit + native vector similarity in one system.                    |
| AI / LLM    | Claude API (primary), OpenAI (fallback)                | Adapter pattern — providers swappable without touching call sites.          |
| Embeddings  | OpenAI `text-embedding-3-small`                        | 1536-dim vectors for pgvector ivfflat ANN index.                            |
| Auth        | JWT + bcrypt                                           | Stateless, portfolio-friendly, easy to explain in interviews.               |
| External    | Google Books, TMDb, Guardian, YouTube Data API v3      | All free tiers, all wrapped in interchangeable adapters.                    |
| Email       | APScheduler + SMTP                                     | Weekly digest cron; provider-agnostic sender behind a Protocol.             |
| Deployment  | Vercel (frontend), Render (backend + Postgres)         | Free tiers, GitHub-integrated auto-deploy, no infrastructure to operate.    |
| CI          | GitHub Actions                                         | Lint + tests + build on every PR; blocking on failures.                     |

Full trade-off justifications for every choice: [docs/02_Technical_Design_Document.docx](docs/02_Technical_Design_Document.docx) §3.

## Architecture

```
Browser
  |
  | HTTPS / JSON
  v
+------------------------------+
|      React SPA (Vercel)      |
+------------------------------+
  |
  v
+------------------------------+       +------------------+
|    FastAPI (Render, Docker)  |------>|  Claude / OpenAI |
|  auth / chat / recs / memory |       +------------------+
|  cross-media / feedback      |       +------------------+
|  digest scheduler            |------>|  Google Books    |
+------------------------------+       |  TMDb / OMDb     |
  |                                    |  Guardian        |
  v                                    |  YouTube Data    |
+------------------------------+       +------------------+
| PostgreSQL 16 + pgvector     |
| users · preferences ·        |
| preference_embeddings ·      |
| chat_sessions · messages ·   |
| recommendations · feedback   |
+------------------------------+
```

Diagrams (system architecture, ER diagram, use case diagram, sequence diagrams, wireframes, WBS) live in [`docs/`](docs/) alongside the planning documents.

## Feature list

**Phase 1 — MVP (shipped week 8):**

- Email + password auth with JWT + bcrypt
- Conversational onboarding chatbot
- Three browsing sections (Books, Articles, Movies)
- AI-generated primary pick with image + description
- Embedded YouTube trailer on movie picks
- Four closely-related "similar" items per pick
- Returning-user personalised greeting
- Feedback loop (love / not-for-me / save / show-another) that adjusts future picks
- Settings page for editing preferences

**Phase 2 — Enhanced (shipped week 14):**

- Mood selector (light / intense / contemplative / fun / dark) that persists across sessions
- Cross-media linking (book → film adaptation → related article)
- pgvector similarity for two-stage recommendation ranking
- Weekly digest email (opt-in) sent every Sunday
- axe-core accessibility audit blocking CI on WCAG AA violations

## Getting started (local development)

Detailed setup and deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Short version:

```bash
git clone https://github.com/Mileperuma/Luminary.git
cd Luminary

# Start Postgres + pgvector
docker compose up -d db

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                                   # fill in API keys
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app is then on `http://localhost:5173`. Backend API docs are at `http://localhost:8000/docs`.

## Testing

```bash
# Backend
cd backend && pytest                       # 57 tests
cd backend && ruff check .                 # lint

# Frontend
cd frontend && npm test                    # 7 tests including axe-core a11y
cd frontend && npm run lint
cd frontend && npm run build
```

Backend coverage is ≥ 70 %; targets and details are in [docs/PHASE_1_ACCEPTANCE.md](docs/PHASE_1_ACCEPTANCE.md).

## Repository layout

```
luminary/
├── backend/                    FastAPI service (Python 3.12)
│   ├── app/
│   │   ├── api/                Route handlers, one file per resource
│   │   ├── core/               Config, db engine, security, scheduler
│   │   ├── models/             SQLModel ORM classes
│   │   ├── services/           Business logic (auth, recommender, chatbot, memory, digest, etc.)
│   │   ├── schemas/            Pydantic request/response shapes
│   │   └── prompts/            LLM prompt templates as Markdown
│   ├── alembic/                DB migrations
│   ├── db/init/                Bootstrap SQL (enables pgvector)
│   ├── tests/                  pytest suite
│   ├── Dockerfile              Multi-stage build; runs migrations on start
│   └── pyproject.toml
├── frontend/                   React + Vite + Tailwind SPA
│   ├── src/
│   │   ├── components/         Reusable UI (RecommendationCard, ChatPanel, MoodSelector, …)
│   │   ├── pages/              Route-level screens
│   │   ├── context/            AuthContext + hook
│   │   └── lib/                API clients (auth, chat, recommendations, memory, feedback, …)
│   ├── vite.config.ts          Dev proxy /api → :8000
│   └── package.json
├── docs/                       Planning docs + runbook + acceptance checklist + retrospective
├── .github/workflows/          CI pipeline
├── docker-compose.yml          Local Postgres + pgvector
├── render.yaml                 Render Blueprint (backend + DB)
└── README.md                   You are here
```

## What I learned

See [docs/RETROSPECTIVE.md](docs/RETROSPECTIVE.md) for the full write-up. Highlights:

- Building the LLM adapter first, before any consumer of it, made providers genuinely swappable and gave every test a `FakeLLMClient` to work against — no monkey-patching SDKs.
- Importing modules (not names) for anything that needs runtime patching. Cost me two failing test runs in Sprint 3 to relearn that lesson.
- pgvector is delightful for portfolio scale. `text-embedding-3-small` gives 1536-dim vectors, ivfflat with `lists = 100` makes ANN lookups sub-millisecond on any reasonable candidate set.
- Doing a full ProdDD / TDD / Project Plan trio before writing code shaped every subsequent trade-off. The MoSCoW split for Phase 1 vs Phase 2 saved me from scope creep at least four times.

## License

[MIT](LICENSE) © Matheesha Peruma

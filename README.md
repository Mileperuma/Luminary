# Luminary

An AI-powered cross-media recommendation assistant for books, articles, and movies.

Luminary helps people decide what to read or watch next. It has three dedicated sections — Books, Articles, and Movies — and uses an AI assistant to learn what you like through a short conversation. Each section returns one strong primary pick (with an image, a short description, and an embedded trailer for movies) plus a row of closely related similar items.

The thing that sets Luminary apart is that it treats your taste as a single profile across all three media types and remembers it across visits. When you come back, the assistant greets you with context — *"Welcome back. You loved slow-burn psychological thrillers last week; here are three new picks in that vein."* — instead of asking you to start from scratch.

## Status

**Phase 0 — planning and scaffolding.** This repository currently contains the planning documents (under `/docs`) and the initial project skeleton. Feature code is being added across the sprints defined in [docs/03_Project_Plan.docx](docs/03_Project_Plan.docx).

## Repository layout

```
luminary/
├── backend/              FastAPI service (Python 3.12)
├── frontend/             React + Vite + Tailwind SPA
├── docs/                 Planning documents (Product Definition, Technical Design, Project Plan)
├── .github/workflows/    CI pipeline
├── docker-compose.yml    Local PostgreSQL + pgvector for development
├── README.md             This file
└── LICENSE               MIT
```

## Tech stack

| Layer       | Choice                                    |
|-------------|-------------------------------------------|
| Frontend    | React 18, Vite, Tailwind CSS, TypeScript  |
| Backend     | FastAPI, Python 3.12, SQLModel            |
| Database    | PostgreSQL 16 with the pgvector extension |
| AI / LLM    | Claude API (primary), OpenAI (fallback)   |
| External    | Google Books, TMDb / OMDb, The Guardian, YouTube Data API |
| Hosting     | Vercel (frontend), Render (backend + DB)  |
| CI          | GitHub Actions                            |

Full justifications for each choice live in [docs/02_Technical_Design_Document.docx](docs/02_Technical_Design_Document.docx) Section 3.

## Getting started (local development)

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for the local PostgreSQL container)
- A Claude API key or OpenAI API key

### 1. Clone and prepare environment files

```bash
git clone <your-repo-url>
cd luminary
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Open both .env files and fill in real values
```

### 2. Start the database

```bash
docker compose up -d db
```

This spins up PostgreSQL 16 with pgvector enabled on `localhost:5432`.

### 3. Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The API is now running on `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive OpenAPI explorer.

### 4. Run the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The SPA is now running on `http://localhost:5173`.

## Running tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Planning documents

| Document                                                              | Purpose                                          |
|-----------------------------------------------------------------------|--------------------------------------------------|
| [docs/01_Product_Definition_Document.docx](docs/01_Product_Definition_Document.docx) | Problem, users, requirements, success metrics    |
| [docs/02_Technical_Design_Document.docx](docs/02_Technical_Design_Document.docx)     | Architecture, tech stack, data model, API design |
| [docs/03_Project_Plan.docx](docs/03_Project_Plan.docx)                | WBS, timeline, risks, definition of done         |

## Contributing

This is a portfolio project, so contributions aren't accepted — but issues and suggestions are welcome.

## License

[MIT](LICENSE) © Matheesha Peruma

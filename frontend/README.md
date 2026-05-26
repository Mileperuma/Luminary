# Luminary frontend

React + Vite + TypeScript + Tailwind SPA.

## Quick start

```bash
# from /frontend
npm install
cp .env.example .env
npm run dev
```

The app is now on `http://localhost:5173`. Calls to `/api/*` are proxied to the FastAPI backend on port 8000 (see `vite.config.ts`).

## Scripts

| Script             | Purpose                                |
|--------------------|----------------------------------------|
| `npm run dev`      | Vite dev server with HMR.              |
| `npm run build`    | Type-check and build for production.   |
| `npm run preview`  | Serve the production build locally.    |
| `npm run lint`     | Lint TypeScript with ESLint.           |
| `npm test`         | Run the Vitest test suite once.        |
| `npm run test:watch` | Re-run tests on file change.         |

## Layout

```
frontend/
├── src/
│   ├── main.tsx          App entry point
│   ├── App.tsx           Root component (placeholder for Phase 0)
│   ├── index.css         Tailwind + base styles
│   ├── lib/api.ts        Axios client with JWT interceptor
│   ├── components/       Reusable UI (will grow in Sprint 1+)
│   ├── pages/            Route-level screens (will grow in Sprint 1+)
│   └── test/setup.ts     Test setup (jest-dom matchers)
├── public/               Static assets
├── index.html            HTML shell with Inter + Fraunces fonts
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js    Calm light theme — see Doc 2 Section 9.1
├── postcss.config.js
├── .eslintrc.cjs
└── .env.example
```

## Design notes

The colour palette and typography are locked to the visual style guide in `docs/02_Technical_Design_Document.docx` Section 9.1. The whole UI is built on six named colours (`cream`, `ink`, `muted`, `accent`, `card`, `line`) defined in `tailwind.config.js`. Stick to those — no inline hex values.

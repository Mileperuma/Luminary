# Phase 1 acceptance checklist

Run through this manually after every deploy. Every box ticked = M5 met.
Each item maps to a functional requirement (FR-XX) from
`01_Product_Definition_Document.docx` Section 8.

## Account + identity

- [ ] **FR-01** New user can register via the `/register` page with email + display name + password ≥ 8 characters.
- [ ] **FR-02** Returning user can log in via `/login`; logging out clears the JWT and redirects to `/`.
- [ ] Refreshing the page after sign-in keeps the session alive (`GET /api/auth/me` succeeds).

## Onboarding

- [ ] **FR-03** A brand-new user lands on `/home` and sees an onboarding nudge.
- [ ] Clicking "Start chat" opens `/onboarding`.
- [ ] The chatbot asks short focused questions (≤ 10 turns) and saves preferences at the end.
- [ ] After saving, the user is offered a link to "See my picks" and returns to `/home`.

## Browsing

- [ ] **FR-04** `/home` exposes three section links: Books, Articles, Movies.
- [ ] **FR-05** Each section page returns recommendations restricted to that media type only.

## Recommendation card

- [ ] **FR-06** Each section's primary pick shows a cover/poster/article image.
- [ ] **FR-07** The Movies section displays an embedded YouTube trailer when a key is present.
- [ ] **FR-08** Each recommendation includes a short LLM-written description (~60-80 words).
- [ ] **FR-09** At least four similar items render in a strip below the primary pick.

## Memory + return visits

- [ ] **FR-10** Preferences captured during onboarding are visible at `/settings`.
- [ ] **FR-11** A returning user's `/home` greeting names a specific taste signal (genre, theme, etc.).
- [ ] After a long absence (30+ days) the greeting acknowledges it gently.
- [ ] The "Recent picks" strip on `/home` shows up to three previous recommendations.

## Feedback loop

- [ ] **FR-12** Each recommendation card shows four feedback buttons: Love it / Not for me / Save / Show another.
- [ ] **FR-13** Clicking Love or Not for me visibly adjusts the next recommendation (verified by clicking Show another and observing a different pick).

## Quality bar

- [ ] **NFR-01** P95 latency of `POST /api/recommendations` is ≤ 3 s under normal traffic.
- [ ] **NFR-02** `/home` is interactive within 2 s on a 4G connection.
- [ ] **NFR-04** Production uptime ≥ 99.0% over the demo window.
- [ ] **NFR-05** Passwords are bcrypt-hashed; no plaintext in any log or response.
- [ ] **NFR-06** All traffic is HTTPS; no secrets committed to the repo (`grep -ri "sk-" backend/` returns nothing).
- [ ] **NFR-08** WCAG AA contrast verified by axe-core in CI (`npm test` includes `a11y.test.tsx`).
- [ ] **NFR-10** Backend test coverage ≥ 70% (`pytest --cov=app`).
- [ ] **NFR-11** OpenAPI docs at `/docs` are auto-generated and accurate.

## Deployment

- [ ] Public Render URL serves the backend; `/api/health` returns `{"status":"ok"}`.
- [ ] Public Vercel URL serves the frontend; CORS allows the Vercel origin.
- [ ] `alembic upgrade head` ran cleanly on the latest deploy (no unapplied migrations).
- [ ] CI on `main` is green for both jobs.

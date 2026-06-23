# VISTA Backend Refactor Plan (Node.js → Python)

## Goal

Replace the monolithic Node.js backend (`vista-backend/server.js`, ~1320 lines) with a modular Python backend while **keeping the frontend API contract unchanged**.

The frontend (`vistapj/index.html`, `vistapj/remote.html`) calls fixed paths under `/api/*`. Python must return the same JSON shapes and HTTP status codes.

## Current State

| Item | Detail |
|------|--------|
| Runtime | Node.js + Express 5 |
| Structure | Single file (`server.js`) |
| Persistence | In-memory `Map` for remote sessions |
| Database | None |
| Tests | None |
| Static assets | Serves `vistapj/` from backend |

## Target State

| Item | Detail |
|------|--------|
| Runtime | Python 3.11+ + FastAPI + Uvicorn |
| Structure | `routes/` + `services/` + `utils/` |
| Persistence | In-memory session store (same behavior as Node) |
| Tests | pytest for routes and intent parsing |
| Static assets | FastAPI `StaticFiles` for `vistapj/` |

## Migration Principles

1. **API paths unchanged** — no frontend edits required for basic migration.
2. **JSON field names unchanged** — e.g. `{ images }`, `{ image }`, `{ session, code }`.
3. **Migrate in layers** — session → proxies → generation → agent.
4. **Document before moving** — see `API_CONTRACT.md` and `ENVIRONMENT.md`.
5. **Keep Node backend** until Python parity is verified.

## Phases

### Phase 0 — Documentation (this PR)

- [x] Backend map and API contract
- [x] Environment variable reference
- [x] Python project scaffold

### Phase 1 — Session + health (low risk)

Routes:

- `GET /`
- `POST /api/session`
- `GET /api/session/{id}`
- `POST /api/cmd`
- `GET /api/check`
- `GET /api/status`

No external APIs. Good first migration target.

### Phase 2 — Image search + weather (medium risk)

Routes:

- `GET /api/unsplash`
- `GET /api/pexels`
- `GET /api/pixabay`
- `GET /api/weather`

Mostly HTTP proxy logic. Unify error handling and timeouts.

### Phase 3 — AI generation (higher risk)

Routes:

- `POST /api/generate`
- `POST /api/generate_batch`
- `POST /api/openai_image`
- `POST /api/replicate`
- `POST /api/refine`

Replicate routes poll until completion (120s timeout). Needs careful async handling.

### Phase 4 — Agent (highest complexity)

Route:

- `POST /api/agent`

Includes:

- OpenAI Responses API
- Tool definitions and execution
- Text intent fallback (`inferToolFromText`)
- Internal calls to other `/api/*` endpoints

Split into:

- `agent_service.py` — orchestration
- `tool_executor.py` — tool dispatch
- `text_intent.py` — regex/heuristic fallback

### Phase 5 — Speech + hardening

Route:

- `POST /api/transcribe`

Then add:

- Integration tests against mocked providers
- `.env.example` validation
- Optional Redis session store
- CI workflow

## Directory Layout

```text
vista-backend-python/
  app/
    main.py              # FastAPI app, CORS, static files
    config.py            # Settings from env
    routes/
      health.py
      sessions.py
      transcribe.py
      image_search.py
      weather.py
      generation.py
      agent.py
    services/
      session_store.py
      unsplash_service.py
      pexels_service.py
      pixabay_service.py
      weather_service.py
      openai_service.py
      replicate_service.py
      agent_service.py
    utils/
      text_intent.py
      dates.py
  tests/
  pyproject.toml
  .env.example
  README.md
```

## Risks

| Risk | Mitigation |
|------|------------|
| Agent behavior drift | Port `inferToolFromText` and tool schemas verbatim; add tests |
| Replicate polling differences | Match 1200ms interval and 120s timeout |
| OpenAI env var split (`OPENAI_KEY` vs `OPENAI_API_KEY`) | Accept both in config |
| Session loss on restart | Document as MVP limitation; optional Redis later |
| No existing tests | Add pytest route tests before deleting Node backend |

## How to Run Python Backend

```bash
cd vista-backend-python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in keys
uvicorn app.main:app --reload --port 3000
```

Point frontend at `http://localhost:3000` (default when hostname is localhost).

## Definition of Done

- [ ] All `/api/*` routes implemented in Python
- [ ] Manual smoke test with `vistapj/index.html`
- [ ] pytest passes for session, weather query validation, intent parsing
- [ ] README documents migration status
- [ ] Node backend marked deprecated (not deleted until verified)

## Next Actions After This PR

1. Smoke-test each route against the Node backend responses.
2. Run frontend locally with Python backend on port 3000.
3. Add mocked integration tests for OpenAI/Replicate.
4. Deploy Python backend to Render alongside or replacing Node.

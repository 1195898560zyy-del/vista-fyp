# VISTA Backend (Python)

FastAPI rewrite of the original Node.js backend. Same API paths — frontend works without changes.

## Quick start

```bash
cd vista-backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # fill in API keys
python run.py
```

- App: http://localhost:3000
- API docs: http://localhost:3000/docs
- Health: http://localhost:3000/health

## How to read this codebase

**Start here → follow the arrows:**

```
main.py
  └── factory.py          ← wires everything together (best overview)
        ├── routers/      ← HTTP endpoints (thin)
        │     └── services/   ← business logic (thick)
        ├── deps.py       ← shared HttpClient + Settings injection
        ├── errors.py     ← { "error": "..." } format
        └── utils/        ← pure helpers (no I/O)
```

### Suggested reading order

| Order | File | Why |
|-------|------|-----|
| 1 | `app/factory.py` | See how the app is assembled |
| 2 | `app/routers/__init__.py` | Route list + feature grouping |
| 3 | `app/routers/session.py` | Simplest feature — remote control |
| 4 | `app/services/session_store.py` | In-memory queue model |
| 5 | `app/routers/images.py` | Typical proxy pattern |
| 6 | `app/services/unsplash.py` | External API client example |
| 7 | `app/services/agent/orchestrator.py` | Agent main loop |
| 8 | `app/services/agent/executor.py` | Tool → service mapping |

## Project layout

```
app/
├── main.py                 # Entry: app = create_app()
├── factory.py              # App assembly (middleware, routers, static)
├── config.py               # .env → Settings
├── deps.py                 # FastAPI Depends() helpers
├── errors.py               # Consistent error JSON
│
├── routers/                # HTTP layer — one file per feature
│   ├── __init__.py         # ALL_ROUTERS registry
│   ├── session.py          # Remote control
│   ├── images.py           # Unsplash / Pexels / Pixabay
│   ├── weather.py
│   ├── ai.py               # Generate / Replicate / Refine
│   ├── transcribe.py       # Whisper
│   ├── agent.py
│   └── helpers.py          # @handle_service_errors decorator
│
├── services/               # Business logic — no FastAPI imports
│   ├── session_store.py
│   ├── unsplash.py / pexels.py / pixabay.py
│   ├── weather.py
│   ├── openai_client.py
│   ├── replicate_client.py
│   ├── image_search.py
│   └── agent/              # Agent split into focused modules
│       ├── orchestrator.py # Main loop (start here for agent)
│       ├── tools.py        # OpenAI function schemas
│       ├── executor.py     # Run one tool
│       ├── intent.py       # Regex fallback
│       ├── replies.py      # Template replies
│       └── parsing.py      # Parse tool-call JSON
│
├── schemas/                # Pydantic request models
│   ├── session.py
│   ├── agent.py
│   └── ai.py
│
└── utils/                  # Pure helpers
    ├── image_ratio.py
    └── query.py
```

## Design rules

1. **Routers are thin** — validate input, call a service, return JSON.
2. **Services are framework-free** — testable without FastAPI.
3. **Agent calls services directly** — never HTTP-fetch localhost.
4. **Errors always look like** `{ "error": "message" }` for frontend compatibility.

## Legacy

Original Node.js server: `legacy/server.js`

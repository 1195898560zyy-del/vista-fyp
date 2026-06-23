# Python backend

FastAPI replacement for `vista-backend/server.js`.

## Setup

```bash
cd vista-backend-python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env        # add API keys
```

## Run

```bash
uvicorn app.main:app --reload --port 3000
```

Or:

```bash
vista-backend
```

Open `vistapj/index.html` — it defaults to `http://localhost:3000` on localhost.

## Test

```bash
pytest
```

## Docs

- Refactor plan: `../docs/BACKEND_REFACTOR_PLAN.md`
- API contract: `../docs/API_CONTRACT.md`
- Environment: `../docs/ENVIRONMENT.md`

Interactive API docs: http://localhost:3000/docs

## Migration status

| Route | Status |
|-------|--------|
| Session / remote | Implemented |
| Transcribe | Implemented |
| Image search | Implemented |
| Weather | Implemented |
| OpenAI / Replicate generation | Implemented |
| Agent | Implemented |

Node backend (`vista-backend/`) remains for comparison until Python is verified in production.

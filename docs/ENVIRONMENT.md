# VISTA Environment Variables

Copy `vista-backend-python/.env.example` to `.env` and fill in values.

## Server

| Variable | Required | Default | Used by |
|----------|----------|---------|---------|
| `PORT` | No | `3000` | Uvicorn bind port |
| `PUBLIC_BASE_URL` | No | `http://localhost:3000` | Agent tool executor (internal API calls) |

## OpenAI

| Variable | Required | Default | Used by |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes* | — | Transcribe, agent, image gen |
| `OPENAI_KEY` | Alt* | — | Same (Node compat alias) |
| `OPENAI_CHAT_MODEL` | No | `gpt-4o-mini` | Agent Responses API |

\* At least one of `OPENAI_API_KEY` or `OPENAI_KEY` for AI features.

## Image libraries

| Variable | Required | Used by |
|----------|----------|---------|
| `UNSPLASH_KEY` | Yes | `/api/unsplash`, agent search |
| `PEXELS_KEY` | Yes | `/api/pexels`, agent search |
| `PIXABAY_KEY` | Yes | `/api/pixabay`, agent search |

## Weather

| Variable | Required | Used by |
|----------|----------|---------|
| `WEATHER_API_KEY` | Yes | `/api/weather` |

Historical weather (agent tool `get_weather_history`) uses **Open-Meteo** — no API key.

## Replicate

| Variable | Required | Used by |
|----------|----------|---------|
| `REPLICATE_API_TOKEN` | Yes* | `/api/replicate`, `/api/refine`, agent |
| `REPLICATE_API_KEY` | Alt* | Same (Node compat alias) |

## Local development

```bash
cd vista-backend-python
cp .env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload --port 3000
```

Frontend auto-uses `http://localhost:3000` when opened from localhost or `file://`.

Override via URL: `index.html?apiBase=http://localhost:3000`

## Deployment notes

- Set all required keys in Render/Heroku/etc. environment config.
- Set `PUBLIC_BASE_URL` to the public URL (e.g. `https://your-app.onrender.com`) so agent tools call the correct host.
- Do not commit `.env` — it is gitignored.

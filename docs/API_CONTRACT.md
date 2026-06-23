# VISTA API Contract

Reference for the Python backend. Shapes match `vista-backend/server.js`.

Base URL: `http://localhost:3000` (dev) or configured `API_BASE` in frontend.

---

## Health

### `GET /`

**Response:** plain text

```text
VISTA backend is running.
```

---

## Remote session

### `POST /api/session`

**Response 200:**

```json
{
  "session": "ABC123...",
  "code": "VISTA-ABCD"
}
```

### `GET /api/session/{id}`

**Response 200:** `{ "ok": true }`  
**Response 404:** `{ "error": "Session not found" }`

### `POST /api/cmd`

**Body:**

```json
{
  "session": "<session_id>",
  "command": { "type": "...", "...": "..." }
}
```

**Response 200:** `{ "ok": true, "id": "<command_id>" }`  
**Response 400:** `{ "error": "Missing session or command" }`  
**Response 404:** `{ "error": "Session not found" }`

### `GET /api/check?session=<id>`

**Response 200:** `{ "command": null }` or `{ "command": { "id", "status", "ts", ... } }`

### `GET /api/status?session=<id>&id=<command_id>`

**Response 200:** `{ "status": "sent" | "executed" }`

---

## Speech

### `POST /api/transcribe`

**Body:**

```json
{
  "audio": "<base64>",
  "mime": "audio/webm"
}
```

**Response 200:** `{ "text": "..." }`  
**Response 500:** `{ "error": "..." }`

---

## Agent

### `POST /api/agent`

**Body:**

```json
{
  "message": "show me cats",
  "summary": "optional conversation summary",
  "state": {
    "preferred_ratio": "1:1",
    "current_image": "https://..."
  }
}
```

**Response 200:**

```json
{
  "tools": [
    {
      "name": "search_library",
      "args": { "query": "cats", "ratio": "1:1" },
      "result": { "images": ["..."], "source": "multi" }
    }
  ],
  "reply": "Found 30 images."
}
```

Or when no tools:

```json
{
  "tools": [],
  "reply": "Got it. What would you like to do next?"
}
```

**Response 400:** `{ "error": "Missing message" }`  
**Response 500:** `{ "error": "..." }`

### Agent tools (internal)

| Tool | Args | Result |
|------|------|--------|
| `search_library` | `query`, `source?`, `ratio?` | `{ images, source }` |
| `generate_ai` | `prompt`, `count?`, `aspect_ratio?` | `{ images }` |
| `refine_image` | `prompt`, `input_image` | `{ image }` |
| `set_view` | `view` | `{ view }` |
| `refresh_weather` | — | `{ ok: true }` |
| `get_weather_history` | `city`, `date` | `{ city, country, date, temperature_max, ... }` |

---

## Image search

### `GET /api/unsplash?q=&page=&ratio=&random=&w=&h=`

**Response 200:**

```json
{
  "images": ["https://..."],
  "page": 1,
  "totalPages": 10
}
```

### `GET /api/pexels?q=&page=&ratio=&random=`

**Response 200:** `{ "images": ["..."] }`

### `GET /api/pixabay?q=&page=&ratio=&random=`

**Response 200:** `{ "images": ["..."], "totalPages": 5 }`

All return **400** if `q` missing; **500** on provider failure.

---

## Weather

### `GET /api/weather?lat=&lon=`

**Response 200:**

```json
{
  "city": "London",
  "temp": 15.2,
  "description": "clear sky",
  "main": "Clear",
  "icon": "01d",
  "humidity": 60,
  "wind": 3.5,
  "dt": 1710000000,
  "timezone": 3600
}
```

---

## OpenAI image generation

### `POST /api/generate`

**Body:** `{ "prompt", "size?", "model?" }`  
**Response:** OpenAI raw JSON passthrough

### `POST /api/generate_batch`

**Body:** `{ "prompts": ["..."], "size?", "model?" }`  
**Response:** `{ "data": [...], "error": null | "..." }`

### `POST /api/openai_image`

**Body:** `{ "prompt", "size?", "model?", "count?" }`  
**Response:** `{ "images": ["url1", "url2"] }`

---

## Replicate

### `POST /api/replicate`

**Body:** `{ "prompt", "aspect_ratio?", "count?" }`  
**Response:** `{ "images": ["..."], "status": "succeeded" }`

### `POST /api/refine`

**Body:** `{ "prompt", "input_image" }`  
**Response:** `{ "image": "https://..." }`

---

## Common error shape

```json
{ "error": "Human-readable message" }
```

HTTP status: 400 (client), 404 (not found), 500 (server/provider).

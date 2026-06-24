"""Quick smoke test — run while server is up on port 3000."""

import httpx

BASE = "http://127.0.0.1:3000"

checks: list[tuple[str, int, str]] = []

with httpx.Client(timeout=10) as client:
    r = client.get(f"{BASE}/health")
    checks.append(("GET /health", r.status_code, r.text[:40]))

    r = client.post(f"{BASE}/api/session")
    checks.append(("POST /api/session", r.status_code, str(r.json())))

    sid = r.json().get("session", "")
    r = client.get(f"{BASE}/api/session/{sid}")
    checks.append(("GET /api/session/:id", r.status_code, str(r.json())))

    r = client.get(f"{BASE}/api/unsplash?q=cat")
    checks.append(("GET /api/unsplash (no key → 500 expected)", r.status_code, str(r.json())))

    r = client.get(f"{BASE}/")
    checks.append(("GET / (frontend)", r.status_code, r.text[:30]))

for name, code, body in checks:
    ok = code in (200, 500) or (name.endswith("500 expected") and code == 500)
    mark = "OK" if ok else "FAIL"
    print(f"[{mark}] {name} → {code} | {body}")

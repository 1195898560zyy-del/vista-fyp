"""
VISTA Backend — Python/FastAPI application package.

Architecture (top → bottom):
    main.py          → boots the app
    factory.py       → wires middleware, routers, static files
    routers/         → HTTP endpoints (thin: validate input, call services)
    services/        → business logic & third-party API clients
    schemas/         → request/response Pydantic models
    deps.py          → shared FastAPI dependencies (HTTP client, settings)
    errors.py        → consistent { "error": "..." } JSON errors
    utils/           → small pure helpers (no I/O)

Start reading from factory.py, then pick any router and follow the import
into its service module.
"""

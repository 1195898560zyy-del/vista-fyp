"""
Application factory — assembles middleware, routers, and static files.

This is the best single file to read when you want the big picture of how
everything connects.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.errors import register_exception_handlers
from app.routers import ALL_ROUTERS

# vista-backend/app/factory.py → repo root → vistapj/
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "vistapj"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create one shared HTTP client for the whole app lifetime."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        app.state.http_client = client
        yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="VISTA Backend",
        description="Image library, AI generation, and conversational agent API.",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    for router in ALL_ROUTERS:
        app.include_router(router)

    @app.get("/health", response_class=PlainTextResponse, include_in_schema=False)
    async def health() -> str:
        return "VISTA backend is running."

    if FRONTEND_DIR.is_dir():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    # Store settings on app for debugging / future use
    app.state.settings = settings

    configured = [
        name
        for name, ok in [
            ("UNSPLASH", bool(settings.unsplash_key)),
            ("PEXELS", bool(settings.pexels_key)),
            ("PIXABAY", bool(settings.pixabay_key)),
            ("WEATHER", bool(settings.weather_api_key)),
            ("OPENAI", bool(settings.resolved_openai_key)),
            ("REPLICATE", bool(settings.resolved_replicate_token)),
        ]
        if ok
    ]
    if configured:
        print(f"API keys loaded: {', '.join(configured)}")
    else:
        print("WARNING: no API keys found — copy .env.example to .env and fill in keys")

    return app

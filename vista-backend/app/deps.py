"""Shared FastAPI dependencies injected into route handlers."""

from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, Request

from app.config import Settings, get_settings


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Return the shared async HTTP client created in app lifespan."""
    return request.app.state.http_client


HttpClient = Annotated[httpx.AsyncClient, Depends(get_http_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

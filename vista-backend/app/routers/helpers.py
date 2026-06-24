"""Decorator to convert service exceptions into consistent API errors."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from app.errors import api_error

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def handle_service_errors(func: F) -> F:
    """Wrap an async route handler: any uncaught exception → 500 `{ "error": msg }`."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            raise api_error(str(exc), 500) from exc

    return wrapper  # type: ignore[return-value]

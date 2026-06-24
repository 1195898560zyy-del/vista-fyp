"""API error helpers — keep the same JSON shape the frontend expects."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def api_error(message: str, status_code: int = 400) -> HTTPException:
    """Raise an HTTPException whose body is `{ "error": message }`."""
    return HTTPException(status_code=status_code, detail={"error": message})


def register_exception_handlers(app: FastAPI) -> None:
    """Ensure all errors return `{ "error": "..." }`, not FastAPI's default `detail`."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": "Invalid request"})

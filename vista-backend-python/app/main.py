from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import agent, generation, health, image_search, sessions, transcribe, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=120.0)
    yield
    await app.state.http_client.aclose()


app = FastAPI(title="VISTA Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(transcribe.router)
app.include_router(image_search.router)
app.include_router(weather.router)
app.include_router(generation.router)
app.include_router(agent.router)

settings = get_settings()
frontend_dir = settings.frontend_dir
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


def run() -> None:
    s = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=s.port, reload=False)


if __name__ == "__main__":
    run()

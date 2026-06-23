from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.services.openai_service import (
    generate_openai_batch,
    generate_openai_image,
    replicate_generate,
    replicate_refine,
)

router = APIRouter(prefix="/api")


class GenerateBody(BaseModel):
    prompt: str
    size: str | None = None
    model: str | None = None


class GenerateBatchBody(BaseModel):
    prompts: list[str]
    size: str = "1024x1024"
    model: str = "gpt-image-1"


class OpenAIImageBody(BaseModel):
    prompt: str
    size: str | None = None
    model: str | None = None
    count: int | None = None


class ReplicateBody(BaseModel):
    prompt: str
    aspect_ratio: str | None = None
    count: int | None = None


class RefineBody(BaseModel):
    prompt: str
    input_image: str


@router.post("/generate")
async def generate(body: GenerateBody, request: Request) -> dict[str, Any]:
    if not body.prompt:
        raise HTTPException(status_code=400, detail={"error": "Missing prompt"})

    settings = get_settings()
    if not settings.openai_key_resolved:
        raise HTTPException(status_code=500, detail={"error": "Missing OPENAI_KEY"})

    client = request.app.state.http_client
    try:
        return await generate_openai_image(
            client,
            settings,
            prompt=body.prompt,
            size=body.size or "1024x1024",
            model=body.model or "gpt-image-1",
            count=3,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "OpenAI proxy failed"}) from exc


@router.post("/generate_batch")
async def generate_batch(body: GenerateBatchBody, request: Request) -> dict[str, Any]:
    if not body.prompts:
        raise HTTPException(status_code=400, detail={"error": "prompts must be array"})

    settings = get_settings()
    if not settings.openai_key_resolved:
        raise HTTPException(status_code=500, detail={"error": "Missing OPENAI_KEY"})

    client = request.app.state.http_client
    try:
        return await generate_openai_batch(
            client, settings, prompts=body.prompts, size=body.size, model=body.model
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Batch generation failed"}) from exc


@router.post("/openai_image")
async def openai_image(body: OpenAIImageBody, request: Request) -> dict[str, list[str]]:
    if not body.prompt:
        raise HTTPException(status_code=400, detail={"error": "Missing prompt"})

    settings = get_settings()
    if not settings.openai_key_resolved:
        raise HTTPException(status_code=500, detail={"error": "Missing OPENAI_KEY"})

    client = request.app.state.http_client
    try:
        data = await generate_openai_image(
            client,
            settings,
            prompt=body.prompt,
            size=body.size or "1024x1024",
            model=body.model or "gpt-image-1",
            count=body.count or 1,
            response_format="url",
        )
        images = [item.get("url") for item in data.get("data", []) if item.get("url")]
        return {"images": images}
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "OpenAI image proxy failed"}) from exc


@router.post("/replicate")
async def replicate(body: ReplicateBody, request: Request) -> dict[str, Any]:
    if not body.prompt:
        raise HTTPException(status_code=400, detail={"error": "Missing prompt"})

    settings = get_settings()
    client = request.app.state.http_client
    try:
        return await replicate_generate(
            client,
            settings,
            prompt=body.prompt,
            aspect_ratio=body.aspect_ratio or "1:1",
            count=body.count or 1,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Replicate request failed"}) from exc


@router.post("/refine")
async def refine(body: RefineBody, request: Request) -> dict[str, str]:
    if not body.prompt or not body.input_image:
        raise HTTPException(status_code=400, detail={"error": "Missing prompt or input_image"})

    settings = get_settings()
    client = request.app.state.http_client
    try:
        return await replicate_refine(
            client,
            settings,
            prompt=body.prompt,
            input_image=body.input_image,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Refine request failed"}) from exc

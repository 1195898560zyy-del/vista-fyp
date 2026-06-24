"""AI image generation and refinement endpoints."""

from fastapi import APIRouter

from app.deps import HttpClient, SettingsDep
from app.errors import api_error
from app.routers.helpers import handle_service_errors
from app.schemas.ai import (
    GenerateBatchRequest,
    GenerateRequest,
    OpenAIImageRequest,
    RefineRequest,
    ReplicateRequest,
)
from app.services import openai_client, replicate_client

router = APIRouter(prefix="/api", tags=["ai"])


@router.post("/generate")
@handle_service_errors
async def generate(client: HttpClient, settings: SettingsDep, body: GenerateRequest):
    return await openai_client.generate_images(
        client,
        settings,
        prompt=body.prompt,
        size=body.size or "1024x1024",
        model=body.model or "gpt-image-1",
        count=3,
    )


@router.post("/generate_batch")
@handle_service_errors
async def generate_batch(client: HttpClient, settings: SettingsDep, body: GenerateBatchRequest):
    if not body.prompts:
        raise api_error("prompts must be array")
    return await openai_client.generate_images_batch(
        client,
        settings,
        prompts=body.prompts,
        size=body.size,
        model=body.model,
    )


@router.post("/openai_image")
@handle_service_errors
async def openai_image(client: HttpClient, settings: SettingsDep, body: OpenAIImageRequest):
    images = await openai_client.generate_image_urls(
        client,
        settings,
        prompt=body.prompt,
        size=body.size or "1024x1024",
        model=body.model or "gpt-image-1",
        count=body.count or 1,
    )
    return {"images": images}


@router.post("/replicate")
@handle_service_errors
async def replicate_generate(client: HttpClient, settings: SettingsDep, body: ReplicateRequest):
    if not body.prompt:
        raise api_error("Missing prompt")
    return await replicate_client.generate_flux(
        client,
        settings,
        prompt=body.prompt,
        aspect_ratio=body.aspect_ratio or "1:1",
        count=body.count or 1,
    )


@router.post("/refine")
@handle_service_errors
async def refine(client: HttpClient, settings: SettingsDep, body: RefineRequest):
    if not body.prompt or not body.input_image:
        raise api_error("Missing prompt or input_image")
    return await replicate_client.refine_image(
        client,
        settings,
        prompt=body.prompt,
        input_image=body.input_image,
    )

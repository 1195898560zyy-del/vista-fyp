"""Pydantic models for AI image generation endpoints."""

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str
    size: str | None = "1024x1024"
    model: str | None = "gpt-image-1"


class GenerateBatchRequest(BaseModel):
    prompts: list[str]
    size: str = "1024x1024"
    model: str = "gpt-image-1"


class OpenAIImageRequest(BaseModel):
    prompt: str
    size: str | None = "1024x1024"
    model: str | None = "gpt-image-1"
    count: int | None = 1


class ReplicateRequest(BaseModel):
    prompt: str
    aspect_ratio: str | None = "1:1"
    count: int | None = 1


class RefineRequest(BaseModel):
    prompt: str
    input_image: str

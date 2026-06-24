"""Pydantic models for agent and speech endpoints."""

from pydantic import BaseModel


class TranscribeRequest(BaseModel):
    audio: str
    mime: str | None = "audio/webm"


class AgentRequest(BaseModel):
    message: str
    summary: str | None = None
    state: dict | None = None

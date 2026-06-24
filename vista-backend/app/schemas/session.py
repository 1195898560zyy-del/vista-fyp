"""Pydantic models for remote-control endpoints."""

from pydantic import BaseModel


class CmdRequest(BaseModel):
    session: str
    command: dict

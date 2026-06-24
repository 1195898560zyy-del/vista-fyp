"""Conversational agent endpoint — natural language → tool calls → reply."""

from fastapi import APIRouter

from app.deps import HttpClient, SettingsDep
from app.errors import api_error
from app.routers.helpers import handle_service_errors
from app.schemas.agent import AgentRequest
from app.services.agent import run_agent

router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/agent")
@handle_service_errors
async def agent(client: HttpClient, settings: SettingsDep, body: AgentRequest):
    if not body.message:
        raise api_error("Missing message")
    return await run_agent(
        client,
        settings,
        message=body.message,
        summary=body.summary,
        state=body.state,
    )

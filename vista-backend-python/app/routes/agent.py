from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.services.agent_service import run_agent

router = APIRouter(prefix="/api")


class AgentBody(BaseModel):
    message: str
    summary: str | None = None
    state: dict[str, Any] | None = None


@router.post("/agent")
async def agent(body: AgentBody, request: Request) -> dict[str, Any]:
    if not body.message:
        raise HTTPException(status_code=400, detail={"error": "Missing message"})

    settings = get_settings()
    client = request.app.state.http_client
    try:
        return await run_agent(
            client,
            settings,
            message=body.message,
            summary=body.summary,
            state=body.state,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Agent failed"}) from exc

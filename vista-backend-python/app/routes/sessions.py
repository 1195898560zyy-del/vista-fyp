from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.session_store import session_store

router = APIRouter(prefix="/api")


class CmdBody(BaseModel):
    session: str
    command: dict[str, Any]


@router.post("/session")
async def create_session() -> dict[str, str]:
    session_id, code = session_store.create()
    return {"session": session_id, "code": code}


@router.get("/session/{session_id}")
async def validate_session(session_id: str) -> dict[str, bool]:
    if not session_id:
        raise HTTPException(status_code=400, detail={"error": "Missing session id"})
    if not session_store.exists(session_id):
        raise HTTPException(status_code=404, detail={"error": "Session not found"})
    return {"ok": True}


@router.post("/cmd")
async def enqueue_command(body: CmdBody) -> dict[str, Any]:
    if not body.session or not body.command:
        raise HTTPException(status_code=400, detail={"error": "Missing session or command"})
    result = session_store.enqueue_command(body.session, body.command)
    if not result:
        raise HTTPException(status_code=404, detail={"error": "Session not found"})
    cmd_id, _ = result
    return {"ok": True, "id": cmd_id}


@router.get("/check")
async def check_command(session: str = Query(...)) -> dict[str, Any]:
    if not session:
        raise HTTPException(status_code=400, detail={"error": "Missing session"})
    if not session_store.exists(session):
        raise HTTPException(status_code=404, detail={"error": "Session not found"})
    cmd = session_store.pop_command(session)
    return {"command": cmd}


@router.get("/status")
async def command_status(
    session: str = Query(...),
    id: str = Query(...),
) -> dict[str, str]:
    if not session or not id:
        raise HTTPException(status_code=400, detail={"error": "Missing session or id"})
    if not session_store.exists(session):
        raise HTTPException(status_code=404, detail={"error": "Session not found"})
    status = session_store.get_command_status(session, id)
    if not status:
        raise HTTPException(status_code=404, detail={"error": "Command not found"})
    return {"status": status}

"""
Remote control API — lets remote.html send commands to index.html.

Session lifecycle:
  POST /api/session  → create session id + short code
  POST /api/cmd      → remote pushes a command into the session queue
  GET  /api/check    → main page polls and consumes the next command
  GET  /api/status   → optional: check whether a command was executed
"""

from fastapi import APIRouter, Query

from app.errors import api_error
from app.schemas.session import CmdRequest
from app.services.session_store import session_store

router = APIRouter(prefix="/api", tags=["session"])


@router.post("/session")
def create_session():
    session_id, code = session_store.create()
    return {"session": session_id, "code": code}


@router.get("/session/{session_id}")
def get_session(session_id: str):
    if not session_id:
        raise api_error("Missing session id")
    if not session_store.exists(session_id):
        raise api_error("Session not found", 404)
    return {"ok": True}


@router.post("/cmd")
def send_command(body: CmdRequest):
    if not body.session or not body.command:
        raise api_error("Missing session or command")
    if not session_store.exists(body.session):
        raise api_error("Session not found", 404)
    command_id = session_store.enqueue_command(body.session, body.command)
    return {"ok": True, "id": command_id}


@router.get("/check")
def check_commands(session: str = Query(default="")):
    if not session:
        raise api_error("Missing session")
    if not session_store.exists(session):
        raise api_error("Session not found", 404)
    return {"command": session_store.pop_next_command(session)}


@router.get("/status")
def command_status(
    session: str = Query(default=""),
    id: str = Query(default=""),
):
    if not session or not id:
        raise api_error("Missing session or id")
    if not session_store.exists(session):
        raise api_error("Session not found", 404)
    status = session_store.get_command_status(session, id)
    if status is None:
        raise api_error("Command not found", 404)
    return {"status": status}

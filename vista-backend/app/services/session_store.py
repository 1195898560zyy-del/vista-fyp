"""In-memory remote-control session store."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandRecord:
    id: str
    status: str
    ts: int
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "status": self.status, "ts": self.ts, **self.payload}


@dataclass
class Session:
    code: str
    queue: list[CommandRecord] = field(default_factory=list)
    commands: dict[str, CommandRecord] = field(default_factory=dict)
    created_at: int = field(default_factory=lambda: int(time.time() * 1000))


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    @staticmethod
    def _new_session_id() -> str:
        return (f"{int(time.time() * 1000):x}{random.randbytes(3).hex()}").upper()

    @staticmethod
    def _new_short_code() -> str:
        return "VISTA-" + random.randbytes(2).hex().upper()

    @staticmethod
    def _new_command_id() -> str:
        return f"{int(time.time() * 1000):x}_{random.randbytes(4).hex()}"

    def create(self) -> tuple[str, str]:
        session_id = self._new_session_id()
        code = self._new_short_code()
        self._sessions[session_id] = Session(code=code)
        return session_id, code

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def enqueue_command(self, session_id: str, command: dict[str, Any]) -> str:
        session = self._sessions[session_id]
        command_id = self._new_command_id()
        record = CommandRecord(
            id=command_id,
            status="sent",
            ts=int(time.time() * 1000),
            payload=dict(command),
        )
        session.queue.append(record)
        session.commands[command_id] = record
        return command_id

    def pop_next_command(self, session_id: str) -> dict[str, Any] | None:
        session = self._sessions[session_id]
        if not session.queue:
            return None
        record = session.queue.pop(0)
        record.status = "executed"
        session.commands[record.id] = record
        return record.to_dict()

    def get_command_status(self, session_id: str, command_id: str) -> str | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        record = session.commands.get(command_id)
        return record.status if record else None


session_store = SessionStore()

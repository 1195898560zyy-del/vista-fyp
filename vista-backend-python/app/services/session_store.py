import random
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Session:
    code: str
    queue: list[dict[str, Any]] = field(default_factory=list)
    commands: dict[str, dict[str, Any]] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    @staticmethod
    def create_short_code() -> str:
        return "VISTA-" + "".join(
            random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=4)
        ).upper()

    def create(self) -> tuple[str, str]:
        session_id = (
            f"{int(time.time() * 1000):x}"
            f"{''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=6))}"
        ).upper()
        code = self.create_short_code()
        self._sessions[session_id] = Session(code=code)
        return session_id, code

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def enqueue_command(self, session_id: str, command: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
        sess = self.get(session_id)
        if not sess:
            return None
        cmd_id = f"{int(time.time() * 1000):x}_{random.randbytes(4).hex()}"
        record = {
            "id": cmd_id,
            **command,
            "status": "sent",
            "ts": int(time.time() * 1000),
        }
        sess.queue.append(record)
        sess.commands[cmd_id] = record
        return cmd_id, record

    def pop_command(self, session_id: str) -> dict[str, Any] | None:
        sess = self.get(session_id)
        if not sess or not sess.queue:
            return None
        cmd = sess.queue.pop(0)
        cmd["status"] = "executed"
        sess.commands[cmd["id"]] = cmd
        return cmd

    def get_command_status(self, session_id: str, cmd_id: str) -> str | None:
        sess = self.get(session_id)
        if not sess:
            return None
        cmd = sess.commands.get(cmd_id)
        if not cmd:
            return None
        return cmd.get("status")


session_store = SessionStore()

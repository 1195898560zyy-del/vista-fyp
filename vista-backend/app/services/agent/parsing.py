"""Parse tool-call payloads returned by OpenAI."""

from __future__ import annotations

import json
from typing import Any


def parse_tool_args(raw_args: Any) -> dict[str, Any]:
    if isinstance(raw_args, str):
        try:
            return json.loads(raw_args)
        except json.JSONDecodeError:
            return {}
    if isinstance(raw_args, dict):
        return raw_args
    return {}


def tool_name(tool_call: dict[str, Any]) -> str:
    fn = tool_call.get("function") or {}
    return tool_call.get("name") or fn.get("name") or tool_call.get("tool_name") or ""

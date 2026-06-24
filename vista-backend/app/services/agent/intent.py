"""
Regex-based intent fallback when the LLM replies with plain text.

The primary path is OpenAI tool-calling (see orchestrator.py). This module
covers cases where the model does not emit a structured tool call.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any


def _parse_iso_date(text: str) -> str:
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    return match.group(1) if match else ""


def _format_date_offset(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _extract_city(text: str) -> str:
    in_match = re.search(r"\bin\s+([a-z\s]+)$", text, re.I)
    if in_match and in_match.group(1):
        return in_match.group(1).strip()
    weather_match = re.search(r"([a-z\s]+)\s+weather", text, re.I)
    if weather_match and weather_match.group(1):
        return weather_match.group(1).strip()
    zh_match = re.search(r"([\u4e00-\u9fa5A-Za-z\s]+)天气", text)
    if zh_match and zh_match.group(1):
        return zh_match.group(1).strip()
    return ""


def infer_tool_from_text(message: str, state: dict[str, Any] | None) -> dict[str, Any] | None:
    state = state or {}
    text = (message or "").lower().strip()
    if not text:
        return None

    if re.match(r"^(hi|hello|hey|yo|你好|嗨|早上好|下午好|晚上好|早)$", text, re.I):
        return {"reply": "Hi! What would you like to do—search images, generate, or check weather?"}

    if re.search(
        r"refine|edit|retouch|adjust|add|remove|replace|dof|depth of field|blur|bokeh|修|改|调整|虚化|景深|添加|去掉|替换",
        text,
    ):
        if state.get("current_image"):
            return {
                "tools": [
                    {
                        "name": "refine_image",
                        "args": {"prompt": message, "input_image": state["current_image"]},
                    }
                ]
            }
        return {"reply": "Please open an image in the gallery first so I can refine it."}

    if re.search(r"yesterday|last week|last 7 days|过去|昨天|前天|上周", text):
        city = _extract_city(text)
        parsed_date = _parse_iso_date(text)
        if "yesterday" in text or "昨天" in text:
            parsed_date = parsed_date or _format_date_offset(-1)
        elif "前天" in text:
            parsed_date = parsed_date or _format_date_offset(-2)
        elif "last week" in text or "上周" in text:
            parsed_date = parsed_date or _format_date_offset(-7)
        if not city:
            return {"reply": "Which city?"}
        if not parsed_date:
            return {"reply": "Which date should I check?"}
        return {"tools": [{"name": "get_weather_history", "args": {"city": city, "date": parsed_date}}]}

    if re.search(r"show me|search|find|image|picture|photo|搜|搜索|找|图|图片|照片", text) and not re.search(
        r"weather|天气", text
    ):
        query = re.sub(
            r"show me|search|find|images of|image of|pictures of|picture of|photos of|photo of",
            "",
            text,
            flags=re.I,
        )
        query = re.sub(r"搜|搜索|找|图片|照片|图", "", query).strip()
        if not query:
            return {"reply": "What should I search for?"}
        ratio = state.get("preferred_ratio") or state.get("ratio") or "1:1"
        return {"tools": [{"name": "search_library", "args": {"query": query, "ratio": ratio}}]}

    if re.search(r"generate|create|make|draw|生成|画|创作", text):
        prompt = re.sub(r"generate|create|make|draw|生成|画|创作", "", text, flags=re.I).strip()
        if not prompt:
            return {"reply": "What should I generate?"}
        ratio = state.get("preferred_ratio") or state.get("ai_ratio") or "1:1"
        return {"tools": [{"name": "generate_ai", "args": {"prompt": prompt, "aspect_ratio": ratio}}]}

    if not re.search(r"weather|天气", text):
        tokens = text.split()
        if len(tokens) <= 3 and len(text) <= 30:
            ratio = state.get("preferred_ratio") or state.get("ratio") or "1:1"
            return {"tools": [{"name": "search_library", "args": {"query": text, "ratio": ratio}}]}

    return None

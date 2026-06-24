"""OpenAI API helpers."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from app.config import Settings


def _require_openai_key(settings: Settings) -> str:
    key = settings.resolved_openai_key
    if not key:
        raise ValueError("Missing OPENAI_API_KEY")
    return key


async def transcribe_audio(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    audio_b64: str,
    mime: str = "audio/webm",
) -> str:
    api_key = _require_openai_key(settings)
    audio_bytes = base64.b64decode(audio_b64)

    response = await client.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {api_key}"},
        files={"file": ("speech.webm", audio_bytes, mime or "audio/webm")},
        data={"model": "whisper-1", "language": "en"},
    )
    data = response.json()
    if not response.is_success:
        raise RuntimeError(data.get("error", {}).get("message") or "Transcription failed")
    return data.get("text") or ""


async def generate_images(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    size: str = "1024x1024",
    model: str = "gpt-image-1",
    count: int = 3,
) -> dict[str, Any]:
    api_key = _require_openai_key(settings)
    response = await client.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={"prompt": prompt, "n": count, "size": size, "model": model},
    )
    return response.json()


async def generate_images_batch(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompts: list[str],
    size: str = "1024x1024",
    model: str = "gpt-image-1",
) -> dict[str, Any]:
    results: list[Any] = []
    errors: list[str] = []

    for prompt in prompts:
        data = await generate_images(
            client,
            settings,
            prompt=prompt,
            size=size,
            model=model,
            count=1,
        )
        if data.get("data") and data["data"][0]:
            results.append(data["data"][0])
        elif data.get("error"):
            error = data["error"]
            errors.append(error.get("message") if isinstance(error, dict) else str(error))

    return {"data": results, "error": errors[0] if errors else None}


async def generate_image_urls(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    size: str = "1024x1024",
    model: str = "gpt-image-1",
    count: int = 1,
) -> list[str]:
    api_key = _require_openai_key(settings)
    response = await client.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "prompt": prompt,
            "n": count,
            "size": size,
            "model": model,
            "response_format": "url",
        },
    )
    data = response.json()
    if not response.is_success:
        raise RuntimeError(data.get("error", {}).get("message") or "OpenAI image failed")

    return [item["url"] for item in data.get("data", []) if item.get("url")]


async def call_responses_api(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    input_messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    previous_response_id: str | None = None,
) -> dict[str, Any]:
    api_key = _require_openai_key(settings)
    payload: dict[str, Any] = {
        "model": settings.openai_chat_model,
        "input": input_messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.6,
    }
    if previous_response_id:
        payload["previous_response_id"] = previous_response_id

    response = await client.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json=payload,
    )
    data = response.json()
    if not response.is_success:
        raise RuntimeError(data.get("error", {}).get("message") or "OpenAI responses failed")
    return data


def extract_output_text(response: dict[str, Any]) -> str:
    if not response:
        return ""
    output_text = response.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    text = ""
    for item in response.get("output") or []:
        if not item:
            continue
        if item.get("type") == "output_text" and item.get("text"):
            text += item["text"]
        if item.get("type") == "message":
            for part in item.get("content") or []:
                if not part:
                    continue
                if part.get("type") in ("text", "output_text") and part.get("text"):
                    text += part["text"]
    return text


def extract_tool_calls(response: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for item in response.get("output") or []:
        if not item:
            continue
        if item.get("type") in ("tool_call", "function_call"):
            calls.append(item)
        if item.get("type") == "message":
            for part in item.get("content") or []:
                if part and part.get("type") in ("tool_call", "function_call"):
                    calls.append(part)
    return calls

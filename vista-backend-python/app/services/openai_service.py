import asyncio
import base64
import io
import time
from typing import Any

import httpx

from app.config import Settings


async def transcribe_audio(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    audio_b64: str,
    mime: str = "audio/webm",
) -> str:
    api_key = settings.openai_key_resolved
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    buffer = base64.b64decode(audio_b64)
    files = {"file": ("speech.webm", io.BytesIO(buffer), mime or "audio/webm")}
    data = {"model": "whisper-1", "language": "en"}

    r = await client.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {api_key}"},
        files=files,
        data=data,
    )
    body = r.json()
    if not r.is_success:
        raise ValueError(body.get("error", {}).get("message") or "Transcription failed")
    return body.get("text") or ""


async def call_openai_responses(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    input_messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    previous_response_id: str | None = None,
) -> dict[str, Any]:
    api_key = settings.openai_key_resolved
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    payload: dict[str, Any] = {
        "model": settings.openai_chat_model,
        "input": input_messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.6,
    }
    if previous_response_id:
        payload["previous_response_id"] = previous_response_id

    r = await client.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json=payload,
    )
    data = r.json()
    if not r.is_success:
        raise ValueError(data.get("error", {}).get("message") or "OpenAI responses failed")
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
        if item.get("type") == "message" and isinstance(item.get("content"), list):
            for part in item["content"]:
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
        if item.get("type") == "message" and isinstance(item.get("content"), list):
            for part in item["content"]:
                if part and part.get("type") in ("tool_call", "function_call"):
                    calls.append(part)
    return calls


async def generate_openai_image(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    size: str = "1024x1024",
    model: str = "gpt-image-1",
    count: int = 3,
    response_format: str | None = None,
) -> dict[str, Any]:
    if not settings.openai_key_resolved:
        raise ValueError("Missing OPENAI_KEY")

    body: dict[str, Any] = {
        "prompt": prompt,
        "n": count,
        "size": size,
        "model": model,
    }
    if response_format:
        body["response_format"] = response_format

    r = await client.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openai_key_resolved}",
        },
        json=body,
    )
    data = r.json()
    if not r.is_success:
        raise ValueError(data.get("error", {}).get("message") or "OpenAI image failed")
    return data


async def generate_openai_batch(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompts: list[str],
    size: str = "1024x1024",
    model: str = "gpt-image-1",
) -> dict[str, Any]:
    results = []
    errors = []
    for prompt in prompts:
        r = await client.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.openai_key_resolved}",
            },
            json={"prompt": prompt, "n": 1, "size": size, "model": model},
        )
        data = r.json()
        if data.get("data") and data["data"][0]:
            results.append(data["data"][0])
        elif data.get("error"):
            err = data["error"]
            errors.append(err.get("message") if isinstance(err, dict) else str(err))
    return {"data": results, "error": errors[0] if errors else None}


async def _poll_replicate(client: httpx.AsyncClient, token: str, prediction: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    while prediction.get("status") not in ("succeeded", "failed", "canceled"):
        if time.monotonic() - started > 120:
            raise ValueError("Replicate request timed out")
        await asyncio.sleep(1.2)
        poll_url = prediction.get("urls", {}).get("get")
        if not poll_url:
            break
        poll = await client.get(poll_url, headers={"Authorization": f"Bearer {token}"})
        prediction = poll.json()
    return prediction


async def replicate_generate(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    aspect_ratio: str = "1:1",
    count: int = 1,
) -> dict[str, Any]:
    token = settings.replicate_token_resolved
    if not token:
        raise ValueError("Missing REPLICATE_API_TOKEN")

    r = await client.post(
        "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json={"input": {"prompt": prompt, "num_outputs": count, "aspect_ratio": aspect_ratio}},
    )
    prediction = r.json()
    if not r.is_success:
        raise ValueError(prediction.get("error") or "Replicate request failed")

    prediction = await _poll_replicate(client, token, prediction)
    if prediction.get("status") != "succeeded":
        raise ValueError(prediction.get("error") or "Replicate failed")

    output = prediction.get("output") or []
    if not isinstance(output, list):
        output = [output]
    images = [(item.get("url") if isinstance(item, dict) else item) for item in output]
    return {"images": images, "status": prediction.get("status")}


async def replicate_refine(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    input_image: str,
) -> dict[str, str]:
    token = settings.replicate_token_resolved
    if not token:
        raise ValueError("Missing REPLICATE_API_TOKEN")

    r = await client.post(
        "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json={"input": {"prompt": prompt, "input_image": input_image, "output_format": "jpg"}},
    )
    prediction = r.json()
    if not r.is_success:
        raise ValueError(prediction.get("error") or "Replicate request failed")

    prediction = await _poll_replicate(client, token, prediction)
    if prediction.get("status") != "succeeded":
        raise ValueError(prediction.get("error") or "Replicate failed")

    output = prediction.get("output")
    image_url = output.get("url") if isinstance(output, dict) else output
    if not image_url:
        raise ValueError("No output image")
    return {"image": image_url}

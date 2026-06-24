"""Replicate API helpers (Flux Schnell + Kontext Pro)."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from app.config import Settings


def _require_replicate_token(settings: Settings) -> str:
    token = settings.resolved_replicate_token
    if not token:
        raise ValueError("Missing REPLICATE_API_TOKEN")
    return token


async def _poll_prediction(
    client: httpx.AsyncClient,
    token: str,
    prediction: dict[str, Any],
    *,
    timeout_ms: int = 120_000,
    interval_ms: int = 1200,
) -> dict[str, Any]:
    started = time.monotonic() * 1000
    current = prediction

    while current.get("status") not in ("succeeded", "failed", "canceled"):
        if time.monotonic() * 1000 - started > timeout_ms:
            raise RuntimeError("Replicate request timed out")
        await asyncio.sleep(interval_ms / 1000)
        poll_url = current.get("urls", {}).get("get")
        if not poll_url:
            raise RuntimeError("Missing Replicate poll URL")
        response = await client.get(poll_url, headers={"Authorization": f"Bearer {token}"})
        current = response.json()

    if current.get("status") != "succeeded":
        raise RuntimeError(current.get("error") or "Replicate failed")
    return current


def _extract_replicate_error(response: httpx.Response, body: Any) -> str:
    if isinstance(body, dict):
        detail = body.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail
        error = body.get("error")
        if isinstance(error, str) and error.strip():
            return error
        title = body.get("title")
        if isinstance(title, str) and title.strip():
            return title
    return f"Replicate HTTP {response.status_code}"


def _validate_token_format(token: str) -> None:
    if not token.startswith("r8_"):
        raise ValueError(
            "Invalid REPLICATE_API_TOKEN format — copy a token starting with r8_ from "
            "https://replicate.com/account/api-tokens"
        )


async def generate_flux(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    aspect_ratio: str = "1:1",
    count: int = 1,
) -> dict[str, Any]:
    token = _require_replicate_token(settings)
    _validate_token_format(token)
    response = await client.post(
        "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "input": {
                "prompt": prompt,
                "num_outputs": count,
                "aspect_ratio": aspect_ratio,
            }
        },
    )
    prediction = response.json()
    if not response.is_success:
        raise RuntimeError(_extract_replicate_error(response, prediction))

    result = await _poll_prediction(client, token, prediction)
    output = result.get("output") or []
    images = [item.get("url") if isinstance(item, dict) and item.get("url") else item for item in output]
    return {"images": images, "status": result.get("status")}


async def refine_image(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    prompt: str,
    input_image: str,
) -> dict[str, str]:
    token = _require_replicate_token(settings)
    _validate_token_format(token)
    response = await client.post(
        "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "input": {
                "prompt": prompt,
                "input_image": input_image,
                "output_format": "jpg",
            }
        },
    )
    prediction = response.json()
    if not response.is_success:
        raise RuntimeError(_extract_replicate_error(response, prediction))

    result = await _poll_prediction(client, token, prediction)
    output = result.get("output")
    image_url = output.get("url") if isinstance(output, dict) and output.get("url") else output
    if not image_url:
        raise RuntimeError("No output image")
    return {"image": image_url}

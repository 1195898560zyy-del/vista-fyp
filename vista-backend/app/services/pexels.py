"""Pexels image search proxy."""

from __future__ import annotations

import random
from urllib.parse import quote

import httpx

from app.config import Settings
from app.utils.image_ratio import pexels_orientation


async def search_pexels(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    query: str,
    page: int = 1,
    random: bool = False,
    ratio: str = "",
) -> dict:
    if not settings.pexels_key:
        raise ValueError("Missing PEXELS_KEY")

    pick_page = random.randint(1, 50) if random else page
    orientation = pexels_orientation(ratio)
    orientation_param = f"&orientation={orientation}" if orientation else ""

    url = (
        "https://api.pexels.com/v1/search"
        f"?query={quote(query)}&per_page=30&page={pick_page}{orientation_param}"
    )
    headers = {"Authorization": settings.pexels_key}

    response = await client.get(url, headers=headers)
    if not response.is_success:
        raise RuntimeError(f"Pexels {response.status_code}: {response.text}")

    data = response.json()
    images = [photo["src"]["large"] for photo in data.get("photos", []) if photo.get("src")]

    if random and not images:
        retry = await client.get(
            f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=30&page=1{orientation_param}",
            headers=headers,
        )
        if not retry.is_success:
            raise RuntimeError(f"Pexels {retry.status_code}: {retry.text}")
        data = retry.json()
        images = [photo["src"]["large"] for photo in data.get("photos", []) if photo.get("src")]

    return {"images": images}

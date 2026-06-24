"""Unsplash image search proxy."""

from __future__ import annotations

from urllib.parse import quote

import httpx

from app.config import Settings
from app.utils.image_ratio import unsplash_orientation


async def search_unsplash(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    query: str,
    page: int = 1,
    random: bool = False,
    ratio: str = "",
    width: int = 0,
    height: int = 0,
) -> dict:
    if not settings.unsplash_key:
        raise ValueError("Missing UNSPLASH_KEY")

    per_page = 30
    orientation = unsplash_orientation(ratio)
    orientation_param = f"&orientation={orientation}" if orientation else ""

    if random:
        url = (
            "https://api.unsplash.com/photos/random"
            f"?query={quote(query)}&count={per_page}{orientation_param}"
            f"&client_id={settings.unsplash_key}"
        )
    else:
        url = (
            "https://api.unsplash.com/search/photos"
            f"?query={quote(query)}&page={page}&per_page={per_page}{orientation_param}"
            f"&client_id={settings.unsplash_key}"
        )

    response = await client.get(url)
    data = response.json()

    if data.get("errors"):
        raise RuntimeError(str(data["errors"]))

    results = data if isinstance(data, list) else data.get("results", [])
    images: list[str] = []
    for item in results:
        if not item or not item.get("urls"):
            continue
        if width > 0 and item["urls"].get("raw"):
            height_param = f"&h={height}" if height > 0 else ""
            images.append(
                f"{item['urls']['raw']}&w={width}{height_param}&auto=format&fit=crop"
            )
        else:
            images.append(item["urls"]["regular"])

    return {
        "images": images,
        "page": 1 if random else page,
        "totalPages": 1 if random else data.get("total_pages", 1),
    }

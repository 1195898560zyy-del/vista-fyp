"""Pixabay image search proxy."""

from __future__ import annotations

import math
import random
from urllib.parse import quote

import httpx

from app.config import Settings
from app.utils.image_ratio import pixabay_orientation


async def search_pixabay(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    query: str,
    page: int = 1,
    random: bool = False,
    ratio: str = "",
) -> dict:
    if not settings.pixabay_key:
        raise ValueError("Missing PIXABAY_KEY")

    pick_page = random.randint(1, 50) if random else page
    orientation = pixabay_orientation(ratio)
    orientation_param = f"&orientation={orientation}" if orientation else ""

    url = (
        "https://pixabay.com/api/"
        f"?key={quote(settings.pixabay_key)}"
        f"&q={quote(query)}&image_type=photo&per_page=30&page={pick_page}{orientation_param}"
    )

    response = await client.get(url)
    data = response.json()

    if not response.is_success or data.get("error"):
        raise RuntimeError(data.get("error") or "Pixabay request failed")

    hits = data.get("hits") or []
    images = [
        hit.get("largeImageURL") or hit.get("webformatURL")
        for hit in hits
        if hit.get("largeImageURL") or hit.get("webformatURL")
    ]
    total_hits = int(data.get("totalHits") or 0)
    total_pages = math.ceil(total_hits / 30) if total_hits else 1

    return {"images": images, "totalPages": total_pages}

"""Multi-source image search used by the agent."""

from __future__ import annotations

import asyncio

import httpx

from app.config import Settings
from app.services import pexels, pixabay, unsplash


async def search_library(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    query: str,
    source: str = "multi",
    ratio: str = "1:1",
) -> dict:
    if not query:
        raise ValueError("Missing query")

    selected = source if source in ("multi", "unsplash", "pexels", "pixabay") else "multi"
    ratio_value = ratio or "1:1"

    async def fetch_unsplash() -> list[str]:
        data = await unsplash.search_unsplash(
            client, settings, query=query, random=True, ratio=ratio_value
        )
        return data.get("images") or []

    async def fetch_pexels() -> list[str]:
        data = await pexels.search_pexels(
            client, settings, query=query, random=True, ratio=ratio_value
        )
        return data.get("images") or []

    async def fetch_pixabay() -> list[str]:
        data = await pixabay.search_pixabay(
            client, settings, query=query, random=True, ratio=ratio_value
        )
        return data.get("images") or []

    if selected == "multi":
        results = await asyncio.gather(
            fetch_unsplash(), fetch_pexels(), fetch_pixabay(), return_exceptions=True
        )
        images: list[str] = []
        for result in results:
            if isinstance(result, list):
                images.extend(result)
        return {"images": images, "source": "multi"}

    if selected == "unsplash":
        return {"images": await fetch_unsplash(), "source": selected}
    if selected == "pexels":
        return {"images": await fetch_pexels(), "source": selected}
    if selected == "pixabay":
        return {"images": await fetch_pixabay(), "source": selected}

    raise ValueError("Unsupported source")

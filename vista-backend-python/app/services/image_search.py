import random as rand
from urllib.parse import quote

import httpx

from app.config import Settings


def ratio_to_orientation(ratio: str, provider: str) -> str:
    if ratio.startswith("1:1"):
        if provider == "unsplash":
            return "squarish"
        if provider == "pexels":
            return "square"
        return ""
    if ratio in ("4:3", "16:9"):
        if provider == "unsplash":
            return "landscape"
        if provider == "pexels":
            return "landscape"
        return "horizontal"
    if ratio in ("3:4", "9:16"):
        if provider == "unsplash":
            return "portrait"
        if provider == "pexels":
            return "portrait"
        return "vertical"
    return ""


async def search_unsplash(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    q: str,
    page: int = 1,
    random: bool = False,
    ratio: str = "",
    width: int = 0,
    height: int = 0,
) -> dict:
    per_page = 30
    orientation = ratio_to_orientation(ratio, "unsplash")
    orientation_param = f"&orientation={orientation}" if orientation else ""

    if random:
        url = (
            f"https://api.unsplash.com/photos/random?query={quote(q)}"
            f"&count={per_page}{orientation_param}&client_id={settings.unsplash_key}"
        )
    else:
        url = (
            f"https://api.unsplash.com/search/photos?query={quote(q)}"
            f"&page={page}&per_page={per_page}{orientation_param}&client_id={settings.unsplash_key}"
        )

    r = await client.get(url)
    data = r.json()
    if data.get("errors"):
        raise ValueError(str(data["errors"]))

    results = data if isinstance(data, list) else data.get("results", [])
    images = []
    for item in results:
        if not item or not item.get("urls"):
            continue
        if width > 0 and item["urls"].get("raw"):
            h_param = f"&h={height}" if height > 0 else ""
            images.append(f"{item['urls']['raw']}&w={width}{h_param}&auto=format&fit=crop")
        else:
            images.append(item["urls"]["regular"])

    return {
        "images": images,
        "page": 1 if random else page,
        "totalPages": 1 if random else data.get("total_pages", 1),
    }


async def search_pexels(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    q: str,
    page: int = 1,
    random: bool = False,
    ratio: str = "",
) -> dict:
    pick_page = rand.randint(1, 50) if random else page
    orientation = ratio_to_orientation(ratio, "pexels")
    orientation_param = f"&orientation={orientation}" if orientation else ""
    url = (
        f"https://api.pexels.com/v1/search?query={quote(q)}"
        f"&per_page=30&page={pick_page}{orientation_param}"
    )

    r = await client.get(url, headers={"Authorization": settings.pexels_key})
    if not r.is_success:
        raise ValueError(f"Pexels {r.status_code}: {r.text}")

    data = r.json()
    images = [p["src"]["large"] for p in data.get("photos", []) if p.get("src")]

    if random and not images:
        retry = await client.get(
            f"https://api.pexels.com/v1/search?query={quote(q)}"
            f"&per_page=30&page=1{orientation_param}",
            headers={"Authorization": settings.pexels_key},
        )
        if not retry.is_success:
            raise ValueError(f"Pexels {retry.status_code}: {retry.text}")
        data = retry.json()
        images = [p["src"]["large"] for p in data.get("photos", []) if p.get("src")]

    return {"images": images}


async def search_pixabay(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    q: str,
    page: int = 1,
    random: bool = False,
    ratio: str = "",
) -> dict:
    import random as rand

    if not settings.pixabay_key:
        raise ValueError("Missing PIXABAY_KEY")

    pick_page = rand.randint(1, 50) if random else page
    orientation = ratio_to_orientation(ratio, "pixabay")
    orientation_param = f"&orientation={orientation}" if orientation else ""
    url = (
        f"https://pixabay.com/api/?key={settings.pixabay_key}"
        f"&q={quote(q)}"
        f"&image_type=photo&per_page=30&page={pick_page}{orientation_param}"
    )

    r = await client.get(url)
    data = r.json()
    if not r.is_success or data.get("error"):
        raise ValueError(data.get("error") or "Pixabay request failed")

    images = [
        hit.get("largeImageURL") or hit.get("webformatURL")
        for hit in data.get("hits", [])
        if isinstance(hit, dict)
    ]
    images = [img for img in images if img]
    total_hits = int(data.get("totalHits") or 0)
    total_pages = (total_hits + 29) // 30 if total_hits else 1
    return {"images": images, "totalPages": total_pages}

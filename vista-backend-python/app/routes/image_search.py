from fastapi import APIRouter, HTTPException, Query, Request

from app.config import get_settings
from app.services.image_search import search_pexels, search_pixabay, search_unsplash

router = APIRouter(prefix="/api")


@router.get("/unsplash")
async def unsplash(
    request: Request,
    q: str | None = Query(None),
    page: int = Query(1),
    random: str = Query("0"),
    ratio: str = Query(""),
    w: int = Query(0),
    h: int = Query(0),
) -> dict:
    if not q:
        raise HTTPException(status_code=400, detail={"error": "Missing ?q="})

    settings = get_settings()
    client = request.app.state.http_client
    is_random = random in ("1", "true")
    try:
        return await search_unsplash(
            client,
            settings,
            q=q,
            page=page,
            random=is_random,
            ratio=ratio,
            width=w,
            height=h,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Unsplash proxy failed"}) from exc


@router.get("/pexels")
async def pexels(
    request: Request,
    q: str | None = Query(None),
    page: int = Query(1),
    random: str = Query("0"),
    ratio: str = Query(""),
) -> dict:
    if not q:
        raise HTTPException(status_code=400, detail={"error": "Missing ?q="})

    settings = get_settings()
    client = request.app.state.http_client
    is_random = random in ("1", "true")
    try:
        return await search_pexels(
            client, settings, q=q, page=page, random=is_random, ratio=ratio
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Pexels proxy failed"}) from exc


@router.get("/pixabay")
async def pixabay(
    request: Request,
    q: str | None = Query(None),
    page: int = Query(1),
    random: str = Query("0"),
    ratio: str = Query(""),
) -> dict:
    if not q:
        raise HTTPException(status_code=400, detail={"error": "Missing ?q="})

    settings = get_settings()
    client = request.app.state.http_client
    is_random = random in ("1", "true")
    try:
        return await search_pixabay(
            client, settings, q=q, page=page, random=is_random, ratio=ratio
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Pixabay proxy failed"}) from exc

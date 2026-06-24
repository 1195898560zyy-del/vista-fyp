"""Image library proxy endpoints — hide API keys from the browser."""

from fastapi import APIRouter, Query

from app.deps import HttpClient, SettingsDep
from app.errors import api_error
from app.routers.helpers import handle_service_errors
from app.services import pexels, pixabay, unsplash
from app.utils.query import parse_bool_flag

router = APIRouter(prefix="/api", tags=["images"])


@router.get("/unsplash")
@handle_service_errors
async def unsplash_search(
    client: HttpClient,
    settings: SettingsDep,
    q: str = Query(default=""),
    page: int = Query(default=1),
    random: str = Query(default=""),
    ratio: str = Query(default=""),
    w: int = Query(default=0),
    h: int = Query(default=0),
):
    if not q:
        raise api_error("Missing ?q=")
    return await unsplash.search_unsplash(
        client,
        settings,
        query=q,
        page=page,
        random=parse_bool_flag(random),
        ratio=ratio,
        width=w,
        height=h,
    )


@router.get("/pexels")
@handle_service_errors
async def pexels_search(
    client: HttpClient,
    settings: SettingsDep,
    q: str = Query(default=""),
    page: int = Query(default=1),
    random: str = Query(default=""),
    ratio: str = Query(default=""),
):
    if not q:
        raise api_error("Missing ?q=")
    return await pexels.search_pexels(
        client,
        settings,
        query=q,
        page=page,
        random=parse_bool_flag(random),
        ratio=ratio,
    )


@router.get("/pixabay")
@handle_service_errors
async def pixabay_search(
    client: HttpClient,
    settings: SettingsDep,
    q: str = Query(default=""),
    page: int = Query(default=1),
    random: str = Query(default=""),
    ratio: str = Query(default=""),
):
    if not q:
        raise api_error("Missing ?q=")
    return await pixabay.search_pixabay(
        client,
        settings,
        query=q,
        page=page,
        random=parse_bool_flag(random),
        ratio=ratio,
    )

from fastapi import APIRouter, HTTPException, Query, Request

from app.config import get_settings
from app.services.weather_service import get_current_weather

router = APIRouter(prefix="/api")


@router.get("/weather")
async def weather(
    request: Request,
    lat: float | None = Query(None),
    lon: float | None = Query(None),
) -> dict:
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail={"error": "Missing or invalid lat/lon"})

    settings = get_settings()
    client = request.app.state.http_client
    try:
        return await get_current_weather(client, settings, lat=lat, lon=lon)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Weather proxy failed"}) from exc

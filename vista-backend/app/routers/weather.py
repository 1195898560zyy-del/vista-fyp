"""Live weather proxy — OpenWeatherMap."""

from fastapi import APIRouter, Query

from app.deps import HttpClient, SettingsDep
from app.errors import api_error
from app.routers.helpers import handle_service_errors
from app.services import weather

router = APIRouter(prefix="/api", tags=["weather"])


@router.get("/weather")
@handle_service_errors
async def current_weather(
    client: HttpClient,
    settings: SettingsDep,
    lat: float = Query(default=float("nan")),
    lon: float = Query(default=float("nan")),
):
    if lat != lat or lon != lon:
        raise api_error("Missing or invalid lat/lon")
    return await weather.get_current_weather(client, settings, lat=lat, lon=lon)

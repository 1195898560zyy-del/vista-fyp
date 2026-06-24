"""Weather proxies."""

from __future__ import annotations

from urllib.parse import quote

import httpx

from app.config import Settings


async def get_current_weather(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    lat: float,
    lon: float,
) -> dict:
    if not settings.weather_api_key:
        raise ValueError("Missing WEATHER_API_KEY")

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={quote(str(lat))}&lon={quote(str(lon))}"
        f"&units=metric&appid={quote(settings.weather_api_key)}"
    )
    response = await client.get(url)
    data = response.json()

    if not response.is_success:
        raise RuntimeError(data.get("message") or "Weather request failed")

    info = (data.get("weather") or [{}])[0]
    main = data.get("main") or {}
    wind = data.get("wind") or {}

    return {
        "city": data.get("name"),
        "temp": main.get("temp"),
        "description": info.get("description") or "",
        "main": info.get("main") or "",
        "icon": info.get("icon") or "",
        "humidity": main.get("humidity"),
        "wind": wind.get("speed"),
        "dt": data.get("dt"),
        "timezone": data.get("timezone"),
    }


async def get_weather_history(
    client: httpx.AsyncClient,
    *,
    city: str,
    date: str,
) -> dict:
    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(city)}&count=1&language=en&format=json"
    )
    geo_response = await client.get(geo_url)
    geo_data = geo_response.json()

    results = geo_data.get("results") or []
    if not geo_response.is_success or not results:
        raise RuntimeError("City not found")

    place = results[0]
    lat = place["latitude"]
    lon = place["longitude"]
    day = str(date)[:10]

    history_url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={quote(str(lat))}&longitude={quote(str(lon))}"
        f"&start_date={quote(day)}&end_date={quote(day)}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        "&timezone=auto"
    )
    history_response = await client.get(history_url)
    history_data = history_response.json()

    if not history_response.is_success or not history_data.get("daily"):
        raise RuntimeError("Weather history failed")

    daily = history_data["daily"]
    return {
        "city": place.get("name"),
        "country": place.get("country") or "",
        "date": day,
        "temperature_max": (daily.get("temperature_2m_max") or [None])[0],
        "temperature_min": (daily.get("temperature_2m_min") or [None])[0],
        "precipitation_sum": (daily.get("precipitation_sum") or [None])[0],
        "windspeed_max": (daily.get("windspeed_10m_max") or [None])[0],
    }

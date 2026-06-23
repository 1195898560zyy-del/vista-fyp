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
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&units=metric&appid={settings.weather_api_key}"
    )
    r = await client.get(url)
    data = r.json()
    if not r.is_success:
        raise ValueError(data.get("message") or "Weather request failed")

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


async def get_weather_history(client: httpx.AsyncClient, *, city: str, date: str) -> dict:
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(city)}&count=1&language=en&format=json"
    )
    geo_res = await client.get(geo_url)
    geo_data = geo_res.json()
    results = geo_data.get("results") or []
    if not geo_res.is_success or not results:
        raise ValueError("City not found")

    place = results[0]
    lat = place["latitude"]
    lon = place["longitude"]
    day = str(date)[:10]
    history_url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={day}&end_date={day}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
    )
    history_res = await client.get(history_url)
    history_data = history_res.json()
    if not history_res.is_success or not history_data.get("daily"):
        raise ValueError("Weather history failed")

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

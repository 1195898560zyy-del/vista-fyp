"""Human-readable fallback replies when the LLM summary step fails."""

from __future__ import annotations

from typing import Any


def fallback_reply(tool_results: list[dict[str, Any]]) -> str:
    if not tool_results:
        return ""

    first = tool_results[0]
    name = first.get("name")
    result = first.get("result") or {}

    if name == "get_weather_history" and result.get("city") and result.get("date"):
        max_t = result.get("temperature_max")
        min_t = result.get("temperature_min")
        rain = result.get("precipitation_sum")
        wind = result.get("windspeed_max")
        return (
            f"{result['city']} {result['date']}: "
            f"high {max_t if max_t is not None else '—'}°C, "
            f"low {min_t if min_t is not None else '—'}°C, "
            f"rain {rain if rain is not None else '—'}mm, "
            f"wind {wind if wind is not None else '—'} m/s."
        )

    if name == "refresh_weather":
        return "I have updated the weather data. Do you want today or the past 7 days?"
    if name == "set_view":
        return "View updated."
    if name == "search_library":
        count = len(result.get("images") or [])
        return f"Found {count} images." if count else "Search completed."
    if name == "generate_ai":
        count = len(result.get("images") or [])
        return f"Generated {count} images." if count else "Generation completed."
    if name == "refine_image":
        return "Refine completed."

    return "Done."

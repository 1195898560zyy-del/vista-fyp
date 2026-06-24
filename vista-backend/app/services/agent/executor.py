"""
Execute a single agent tool by calling service modules directly.

Unlike the old Node backend, we never HTTP-fetch our own endpoints here.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.services import image_search, replicate_client, weather
from app.services.agent.parsing import parse_tool_args, tool_name


async def execute_tool(
    client: httpx.AsyncClient,
    settings: Settings,
    tool_call: dict[str, Any],
) -> dict[str, Any]:
    name = tool_name(tool_call)
    args = parse_tool_args(
        tool_call.get("arguments")
        or (tool_call.get("function") or {}).get("arguments")
        or tool_call.get("arguments_json")
        or "{}"
    )

    if name == "search_library":
        return await image_search.search_library(
            client,
            settings,
            query=args.get("query", ""),
            source=args.get("source", "multi"),
            ratio=args.get("ratio", "1:1"),
        )

    if name == "generate_ai":
        if not args.get("prompt"):
            raise ValueError("Missing prompt")
        result = await replicate_client.generate_flux(
            client,
            settings,
            prompt=args["prompt"],
            count=int(args.get("count") or 1),
            aspect_ratio=args.get("aspect_ratio") or "1:1",
        )
        return {"images": result.get("images") or []}

    if name == "refine_image":
        if not args.get("prompt") or not args.get("input_image"):
            raise ValueError("Missing prompt/input_image")
        return await replicate_client.refine_image(
            client,
            settings,
            prompt=args["prompt"],
            input_image=args["input_image"],
        )

    if name == "set_view":
        if not args.get("view"):
            raise ValueError("Missing view")
        return {"view": args["view"]}

    if name == "refresh_weather":
        return {"ok": True}

    if name == "get_weather_history":
        if not args.get("city") or not args.get("date"):
            raise ValueError("Missing city/date")
        return await weather.get_weather_history(
            client, city=args["city"], date=args["date"]
        )

    raise ValueError(f"Unknown tool: {name}")

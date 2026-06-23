import asyncio
import json
from typing import Any

import httpx

from app.config import Settings
from app.services.image_search import search_pexels, search_pixabay, search_unsplash
from app.services.weather_service import get_weather_history
from app.utils.text_intent import infer_tool_from_text


async def execute_tool_call(
    client: httpx.AsyncClient,
    settings: Settings,
    tool_call: dict[str, Any],
) -> dict[str, Any]:
    name = (
        tool_call.get("name")
        or (tool_call.get("function") or {}).get("name")
        or tool_call.get("tool_name")
    )
    raw_args = (
        tool_call.get("arguments")
        or (tool_call.get("function") or {}).get("arguments")
        or tool_call.get("arguments_json")
        or "{}"
    )
    if isinstance(raw_args, str):
        try:
            args = json.loads(raw_args)
        except json.JSONDecodeError:
            args = {}
    elif isinstance(raw_args, dict):
        args = raw_args
    else:
        args = {}

    base_url = settings.public_base_url.rstrip("/")

    if name == "search_library":
        query = args.get("query")
        if not query:
            raise ValueError("Missing query")
        source = args.get("source") or "multi"
        if source not in ("pexels", "unsplash", "pixabay", "multi"):
            source = "multi"
        ratio = args.get("ratio") or "1:1"

        async def fetch_unsplash() -> list[str]:
            data = await search_unsplash(
                client, settings, q=query, random=True, ratio=ratio
            )
            return data.get("images") or []

        async def fetch_pexels() -> list[str]:
            data = await search_pexels(client, settings, q=query, random=True, ratio=ratio)
            return data.get("images") or []

        async def fetch_pixabay() -> list[str]:
            data = await search_pixabay(client, settings, q=query, random=True, ratio=ratio)
            return data.get("images") or []

        if source == "multi":
            u, p, x = await asyncio.gather(
                fetch_unsplash(), fetch_pexels(), fetch_pixabay(), return_exceptions=True
            )
            images = []
            for imgs in (u, p, x):
                if isinstance(imgs, list):
                    images.extend(imgs)
            return {"images": images, "source": "multi"}
        if source == "unsplash":
            return {"images": await fetch_unsplash(), "source": source}
        if source == "pexels":
            return {"images": await fetch_pexels(), "source": source}
        if source == "pixabay":
            return {"images": await fetch_pixabay(), "source": source}
        raise ValueError("Unsupported source")

    if name == "generate_ai":
        prompt = args.get("prompt")
        if not prompt:
            raise ValueError("Missing prompt")
        r = await client.post(
            f"{base_url}/api/replicate",
            json={
                "prompt": prompt,
                "count": args.get("count") or 1,
                "aspect_ratio": args.get("aspect_ratio") or "1:1",
            },
        )
        data = r.json()
        if not r.is_success or data.get("error"):
            raise ValueError(data.get("error") or "Flux failed")
        return {"images": data.get("images") or []}

    if name == "refine_image":
        prompt = args.get("prompt")
        input_image = args.get("input_image")
        if not prompt or not input_image:
            raise ValueError("Missing prompt/input_image")
        r = await client.post(
            f"{base_url}/api/refine",
            json={"prompt": prompt, "input_image": input_image},
        )
        data = r.json()
        if not r.is_success or data.get("error"):
            raise ValueError(data.get("error") or "Refine failed")
        return {"image": data.get("image") or ""}

    if name == "set_view":
        view = args.get("view")
        if not view:
            raise ValueError("Missing view")
        return {"view": view}

    if name == "refresh_weather":
        return {"ok": True}

    if name == "get_weather_history":
        city = args.get("city")
        date = args.get("date")
        if not city or not date:
            raise ValueError("Missing city/date")
        return await get_weather_history(client, city=city, date=date)

    raise ValueError("Unknown tool")


def build_agent_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": "search_library",
            "description": "Search images from the best library source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "source": {"type": "string", "enum": ["multi", "unsplash", "pexels", "pixabay"]},
                    "ratio": {"type": "string", "enum": ["1:1", "4:3", "16:9", "3:4", "9:16"]},
                },
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "set_view",
            "description": "Switch the presenter view between weather and gallery.",
            "parameters": {
                "type": "object",
                "properties": {"view": {"type": "string", "enum": ["weather", "gallery"]}},
                "required": ["view"],
            },
        },
        {
            "type": "function",
            "name": "refresh_weather",
            "description": "Refresh the weather data and wallpaper.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "type": "function",
            "name": "get_weather_history",
            "description": "Get historical daily weather for a city and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["city", "date"],
            },
        },
        {
            "type": "function",
            "name": "generate_ai",
            "description": "Generate images with Flux.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "count": {"type": "integer", "minimum": 1, "maximum": 5},
                    "aspect_ratio": {"type": "string", "enum": ["1:1", "4:3", "16:9", "3:4", "9:16"]},
                },
                "required": ["prompt"],
            },
        },
        {
            "type": "function",
            "name": "refine_image",
            "description": "Refine a single image with Flux Kontext.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "input_image": {"type": "string"},
                },
                "required": ["prompt", "input_image"],
            },
        },
    ]


AGENT_SYSTEM = (
    "You are VISTA Agent. You can chat normally or call a tool. "
    "Use tools only when user intent requires system action. "
    "If required parameters are missing, ask a brief question instead of calling tools. "
    "Do not ask the user which image library to use; choose automatically (default to Unsplash). "
    "If state includes preferred_ratio, use it when ratio/aspect_ratio is missing. "
    "Use set_view to switch between weather and gallery, and refresh_weather to update weather. "
    "If the user asks for historical weather (e.g., yesterday, last week, or a specific date), "
    "call get_weather_history instead of refresh_weather. "
    "After tools run, always produce a natural language reply summarizing results. "
    "Never claim you executed a tool unless you actually called it. "
    "Prefer a single tool call when possible."
)


def fallback_reply(tool_results: list[dict[str, Any]]) -> str:
    if not tool_results:
        return ""
    first = tool_results[0]
    name = first.get("name")
    result = first.get("result") or {}

    if name == "get_weather_history" and result.get("city") and result.get("date"):
        max_t = f"{result['temperature_max']}°C" if result.get("temperature_max") is not None else "—"
        min_t = f"{result['temperature_min']}°C" if result.get("temperature_min") is not None else "—"
        rain = f"{result['precipitation_sum']}mm" if result.get("precipitation_sum") is not None else "—"
        wind = f"{result['windspeed_max']} m/s" if result.get("windspeed_max") is not None else "—"
        return f"{result['city']} {result['date']}: high {max_t}, low {min_t}, rain {rain}, wind {wind}."
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


async def run_agent(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    message: str,
    summary: str | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from app.services.openai_service import (
        call_openai_responses,
        extract_output_text,
        extract_tool_calls,
    )

    tools = build_agent_tools()
    user_context = "\n".join(
        part
        for part in [
            f"Conversation summary: {summary}" if summary else None,
            f"Global state: {json.dumps(state)}" if state else None,
            f"User message: {message}",
        ]
        if part
    )

    first = await call_openai_responses(
        client,
        settings,
        input_messages=[
            {"role": "system", "content": AGENT_SYSTEM},
            {"role": "user", "content": user_context},
        ],
        tools=tools,
    )

    tool_calls = extract_tool_calls(first)
    reply_text = extract_output_text(first)
    state = state or {}

    if not tool_calls:
        inferred = infer_tool_from_text(message, state)
        if inferred and inferred.get("reply"):
            return {"tools": [], "reply": inferred["reply"]}
        if inferred and inferred.get("tools"):
            tool_results = []
            for tool in inferred["tools"]:
                result = await execute_tool_call(
                    client,
                    settings,
                    {"name": tool["name"], "arguments": json.dumps(tool.get("args") or {})},
                )
                tool_results.append({"name": tool["name"], "args": tool.get("args") or {}, "result": result})
            return {
                "tools": tool_results,
                "reply": fallback_reply(tool_results) or "Done.",
            }
        return {
            "tools": [],
            "reply": reply_text or "Got it. What would you like to do next?",
        }

    tool_results = []
    tool_outputs = []
    for call in tool_calls:
        call_id = call.get("id") or call.get("call_id")
        raw_args = call.get("arguments") or call.get("arguments_json") or "{}"
        if isinstance(raw_args, str):
            try:
                tool_args = json.loads(raw_args)
            except json.JSONDecodeError:
                tool_args = {}
        else:
            tool_args = raw_args if isinstance(raw_args, dict) else {}

        tool_name = call.get("name") or (call.get("function") or {}).get("name") or ""
        if tool_name == "refine_image":
            needs_image = not tool_args.get("input_image") or str(tool_args.get("input_image", "")).strip().lower() in (
                "current",
                "current image",
                "current one",
            )
            if needs_image and state.get("current_image"):
                tool_args["input_image"] = state["current_image"]
                call = {**call, "arguments": json.dumps(tool_args)}

        result = await execute_tool_call(client, settings, call)
        tool_results.append({"name": tool_name, "args": tool_args, "result": result})
        if call_id:
            tool_outputs.append({"tool_call_id": call_id, "output": json.dumps(result)})

    second_reply = ""
    try:
        followup_input = [
            {"type": "function_call_output", "call_id": t["tool_call_id"], "output": t["output"]}
            for t in tool_outputs
        ]
        followup_input.append({"role": "user", "content": "Summarize the tool results in a helpful reply."})
        second = await call_openai_responses(
            client,
            settings,
            input_messages=followup_input,
            tools=tools,
            previous_response_id=first.get("id"),
        )
        second_reply = extract_output_text(second)
    except Exception:
        pass

    fb = fallback_reply(tool_results)
    return {
        "tools": tool_results,
        "reply": second_reply or reply_text or fb or "Got it. What would you like to do next?",
    }

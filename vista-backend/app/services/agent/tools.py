"""
Agent tool definitions and system prompt for OpenAI Responses API.

These schemas describe what the LLM is allowed to call. Each tool maps to
a handler in executor.py.
"""

AGENT_TOOLS: list[dict] = [
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

SYSTEM_PROMPT = " ".join(
    [
        "You are VISTA Agent. You can chat normally or call a tool.",
        "Use tools only when user intent requires system action.",
        "If required parameters are missing, ask a brief question instead of calling tools.",
        "Do not ask the user which image library to use; choose automatically (default to Unsplash).",
        "If state includes preferred_ratio, use it when ratio/aspect_ratio is missing.",
        "Use set_view to switch between weather and gallery, and refresh_weather to update weather.",
        "If the user asks for historical weather (e.g., yesterday, last week, or a specific date), call get_weather_history instead of refresh_weather.",
        "After tools run, always produce a natural language reply summarizing results.",
        "Never claim you executed a tool unless you actually called it.",
        "Prefer a single tool call when possible.",
    ]
)

"""
Business logic layer — no FastAPI imports in this package.

Module map:
    session_store.py    Remote control session + command queue (in-memory)
    unsplash.py         Unsplash API client
    pexels.py           Pexels API client
    pixabay.py          Pixabay API client
    weather.py          OpenWeather (live) + Open-Meteo (history)
    openai_client.py    Whisper, image generation, Responses API
    replicate_client.py Flux Schnell + Kontext Pro (with polling)
    image_search.py     Multi-source search helper for the agent
    agent/              Conversational agent (tool-calling loop)
"""

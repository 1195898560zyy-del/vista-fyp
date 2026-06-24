"""
HTTP route modules.

Each file owns one feature area. Handlers should stay thin:
validate input → call a service → return JSON.

ALL_ROUTERS is registered in factory.py in this order.
"""

from app.routers import agent, ai, images, session, transcribe, weather

ALL_ROUTERS = [
    session.router,     # remote control: /api/session, /api/cmd, /api/check
    images.router,      # image libraries: /api/unsplash, /api/pexels, /api/pixabay
    weather.router,     # live weather: /api/weather
    ai.router,          # generation: /api/generate, /api/replicate, /api/refine, …
    transcribe.router,  # speech-to-text: /api/transcribe
    agent.router,       # conversational agent: /api/agent
]

__all__ = ["ALL_ROUTERS", "agent", "ai", "images", "session", "transcribe", "weather"]

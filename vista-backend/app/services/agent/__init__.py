"""
Conversational agent package.

Public entry point: run_agent() in orchestrator.py

Internal modules:
    tools.py        — OpenAI function schemas + system prompt
    intent.py       — regex fallback when LLM returns plain text
    executor.py     — run one tool (search, generate, weather, …)
    replies.py      — template replies if summarization fails
    parsing.py      — normalize tool-call JSON from OpenAI
    orchestrator.py — main loop wiring the above together
"""

from app.services.agent.orchestrator import run_agent

__all__ = ["run_agent"]

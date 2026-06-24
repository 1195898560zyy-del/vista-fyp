"""
Agent orchestration — the main conversation loop.

Flow:
  1. Send user message + system prompt to OpenAI Responses API
  2. If the model returns tool calls → execute each tool → ask model to summarize
  3. If no tool calls → try regex intent fallback → else return plain reply
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import Settings
from app.services import openai_client
from app.services.agent.executor import execute_tool
from app.services.agent.intent import infer_tool_from_text
from app.services.agent.parsing import parse_tool_args, tool_name
from app.services.agent.replies import fallback_reply
from app.services.agent.tools import AGENT_TOOLS, SYSTEM_PROMPT


async def _run_inferred_tools(
    client: httpx.AsyncClient,
    settings: Settings,
    inferred_tools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for tool in inferred_tools:
        result = await execute_tool(
            client,
            settings,
            {"name": tool["name"], "arguments": json.dumps(tool.get("args") or {})},
        )
        results.append({"name": tool["name"], "args": tool.get("args") or {}, "result": result})
    return results


async def _run_llm_tool_calls(
    client: httpx.AsyncClient,
    settings: Settings,
    tool_calls: list[dict[str, Any]],
    state: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    tool_results: list[dict[str, Any]] = []
    tool_outputs: list[dict[str, str]] = []

    for call in tool_calls:
        tool_args = parse_tool_args(call.get("arguments") or call.get("arguments_json") or "{}")
        current_name = tool_name(call)

        if current_name == "refine_image":
            input_image = str(tool_args.get("input_image") or "").strip()
            placeholder = not input_image or re.match(
                r"^(current|current image|current one)$", input_image, re.I
            )
            if placeholder and state.get("current_image"):
                tool_args["input_image"] = state["current_image"]
                call = {**call, "arguments": json.dumps(tool_args)}

        result = await execute_tool(client, settings, call)
        tool_results.append({"name": current_name, "args": tool_args, "result": result})

        call_id = call.get("id") or call.get("call_id")
        if call_id:
            tool_outputs.append({"tool_call_id": call_id, "output": json.dumps(result)})

    return tool_results, tool_outputs


async def _summarize_tool_results(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    first_response_id: str | None,
    tool_outputs: list[dict[str, str]],
) -> str:
    followup_input = [
        {"type": "function_call_output", "call_id": item["tool_call_id"], "output": item["output"]}
        for item in tool_outputs
    ]
    followup_input.append({"role": "user", "content": "Summarize the tool results in a helpful reply."})

    second = await openai_client.call_responses_api(
        client,
        settings,
        input_messages=followup_input,
        tools=AGENT_TOOLS,
        previous_response_id=first_response_id,
    )
    return openai_client.extract_output_text(second)


async def run_agent(
    client: httpx.AsyncClient,
    settings: Settings,
    *,
    message: str,
    summary: str | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}
    user_context = "\n".join(
        part
        for part in [
            f"Conversation summary: {summary}" if summary else None,
            f"Global state: {json.dumps(state)}" if state else None,
            f"User message: {message}",
        ]
        if part
    )

    first = await openai_client.call_responses_api(
        client,
        settings,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_context},
        ],
        tools=AGENT_TOOLS,
    )

    tool_calls = openai_client.extract_tool_calls(first)
    reply_text = openai_client.extract_output_text(first)

    # Path A: no structured tool calls — try regex fallback or plain reply
    if not tool_calls:
        inferred = infer_tool_from_text(message, state)
        if inferred and inferred.get("reply"):
            return {"tools": [], "reply": inferred["reply"]}
        if inferred and inferred.get("tools"):
            tool_results = await _run_inferred_tools(client, settings, inferred["tools"])
            return {
                "tools": tool_results,
                "reply": fallback_reply(tool_results) or "Done.",
            }
        return {"tools": [], "reply": reply_text or "Got it. What would you like to do next?"}

    # Path B: LLM returned tool calls — execute, then summarize
    tool_results, tool_outputs = await _run_llm_tool_calls(client, settings, tool_calls, state)

    second_reply = ""
    if tool_outputs:
        try:
            second_reply = await _summarize_tool_results(
                client,
                settings,
                first_response_id=first.get("id"),
                tool_outputs=tool_outputs,
            )
        except Exception:
            pass

    return {
        "tools": tool_results,
        "reply": second_reply or reply_text or fallback_reply(tool_results) or "Got it. What would you like to do next?",
    }

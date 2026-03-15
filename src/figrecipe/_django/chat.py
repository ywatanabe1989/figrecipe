#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chat endpoint for standalone figrecipe — streams LLM responses via SSE.

Uses anthropic SDK if available, falls back to litellm.
API key read from ANTHROPIC_API_KEY env var.
"""

import json
import logging
import os

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful AI assistant embedded in the FigRecipe figure editor. "
    "Help users create, modify, and understand scientific figures. "
    "You can help with YAML recipe syntax, matplotlib plot types, "
    "data formatting, and figure composition."
)


def _stream_anthropic(prompt: str, history: list):
    """Stream via anthropic SDK."""
    import anthropic

    client = anthropic.Anthropic()
    messages = []
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"
    yield "data: [DONE]\n\n"


def _stream_litellm(prompt: str, history: list):
    """Stream via litellm (multi-provider)."""
    import litellm

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    response = litellm.completion(
        model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-20250514"),
        messages=messages,
        stream=True,
    )
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            yield f"data: {json.dumps({'type': 'chunk', 'text': delta.content})}\n\n"
    yield "data: [DONE]\n\n"


@csrf_exempt
@require_http_methods(["POST"])
def api_chat_stream(request):
    """SSE streaming chat endpoint."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    prompt = data.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"error": "prompt required"}, status=400)

    history = data.get("history", [])

    # Pick backend
    try:
        import anthropic  # noqa: F401

        if os.getenv("ANTHROPIC_API_KEY"):
            generator = _stream_anthropic(prompt, history)
        else:
            raise ImportError("No API key")
    except ImportError:
        try:
            import litellm  # noqa: F401

            generator = _stream_litellm(prompt, history)
        except ImportError:
            return JsonResponse(
                {"error": "No LLM backend available. Set ANTHROPIC_API_KEY."},
                status=503,
            )

    response = StreamingHttpResponse(generator, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response

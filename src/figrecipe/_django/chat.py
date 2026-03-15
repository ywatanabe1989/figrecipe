#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chat endpoint — delegates to scitex-app's shared chat module.

Falls back to a minimal local implementation if scitex-app is not installed.
"""

import json
import logging
import os

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a helpful AI assistant in the FigRecipe figure editor. "
    "Help with YAML recipes, matplotlib plots, and figure composition."
)


@csrf_exempt
@require_http_methods(["POST"])
def api_chat_stream(request):
    """SSE streaming chat — uses scitex-app if available, else anthropic SDK."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    prompt = data.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"error": "prompt required"}, status=400)

    # Try scitex-app shared chat first
    try:
        from scitex_app.chat import sse_keepalive_wrap, stream_chat

        history = data.get("history", [])
        events = stream_chat(
            prompt,
            history=history,
            system_prompt=data.get("system_prompt", _SYSTEM),
        )
        generator = sse_keepalive_wrap(events)
        resp = StreamingHttpResponse(generator, content_type="text/event-stream")
        resp["Cache-Control"] = "no-cache"
        resp["X-Accel-Buffering"] = "no"
        return resp
    except ImportError:
        pass
    except Exception as e:
        logger.warning("scitex-app chat failed: %s, trying fallback", e)

    # Fallback: direct anthropic SDK
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return JsonResponse(
            {"error": "No AI backend. Set ANTHROPIC_API_KEY environment variable."},
            status=503,
        )

    try:
        import anthropic
    except ImportError:
        return JsonResponse(
            {"error": "anthropic package not installed. Run: pip install anthropic"},
            status=503,
        )

    history = data.get("history", [])
    messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
    messages.append({"role": "user", "content": prompt})

    client = anthropic.Anthropic(api_key=api_key)

    def gen():
        try:
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=_SYSTEM,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    resp = StreamingHttpResponse(gen(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp

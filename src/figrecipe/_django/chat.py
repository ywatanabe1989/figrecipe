#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chat endpoint — delegates to scitex-app's shared chat module.

Falls back to a minimal local implementation if scitex-app is not installed.
"""

try:
    from scitex_app.chat import chat_stream_view as api_chat_stream  # noqa: F401
except ImportError:
    # Fallback: minimal SSE chat without scitex-app
    import json
    import logging

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
        """Fallback SSE chat (no scitex-app)."""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        prompt = data.get("prompt", "").strip()
        if not prompt:
            return JsonResponse({"error": "prompt required"}, status=400)

        history = data.get("history", [])
        messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
        messages.append({"role": "user", "content": prompt})

        try:
            import anthropic

            client = anthropic.Anthropic()

            def gen():
                with client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    system=_SYSTEM,
                    messages=messages,
                ) as stream:
                    for text in stream.text_stream:
                        yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"
                yield "data: [DONE]\n\n"

            resp = StreamingHttpResponse(gen(), content_type="text/event-stream")
            resp["Cache-Control"] = "no-cache"
            resp["X-Accel-Buffering"] = "no"
            return resp
        except (ImportError, Exception) as e:
            return JsonResponse(
                {"error": f"Chat unavailable: {e}. Set ANTHROPIC_API_KEY."},
                status=503,
            )

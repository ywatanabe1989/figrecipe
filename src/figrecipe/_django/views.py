#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Views for the figrecipe editor Django app."""

import json
import logging
from pathlib import Path

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .handlers import (
    HANDLERS,
    handle_download_fig,
    handle_single_call,
)
from .services import get_or_create_editor

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).resolve().parent / "static" / "figrecipe"


def _welcome_page(message: str) -> str:
    """Return a simple welcome/error page when no recipe is loaded."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>FigRecipe Editor</title>
<style>
body {{ font-family: -apple-system, sans-serif; background: #1e1e2e;
  color: #e0e0e0; display: flex; align-items: center; justify-content: center;
  height: 100vh; margin: 0; }}
.welcome {{ text-align: center; max-width: 500px; }}
h1 {{ color: #7c5cbf; margin-bottom: 16px; }}
p {{ color: #a0a0b0; line-height: 1.6; }}
code {{ background: #313145; padding: 2px 8px; border-radius: 4px; }}
</style></head>
<body><div class="welcome">
<h1>FigRecipe Editor</h1>
<p>{message}</p>
<p>Example: <code>?recipe=examples/01_line.yaml</code></p>
</div></body></html>"""


def _get_recipe_path(request):
    """Extract recipe_path from request query or body."""
    if request.method == "GET":
        return request.GET.get("recipe", "")
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}
    return data.get("recipe_path", "") or request.GET.get("recipe", "")


def _get_editor(request):
    """Return cached editor for the recipe, or None if no recipe."""
    recipe_path = _get_recipe_path(request)
    if not recipe_path:
        return None
    session_key = f"figrecipe_{recipe_path}"
    try:
        return get_or_create_editor(session_key, recipe_path)
    except FileNotFoundError:
        logger.warning("[FigRecipe] Recipe not found: %s", recipe_path)
        return None


# ── Endpoints that work without an editor ──────────────────────────
_NO_EDITOR_ENDPOINTS = {
    "ping",
    "list_themes",
    "api/tree",
    "api/files",
    "api/switch",
    "api/gallery",
    "api/gallery/add",
    "api/compose",
    "api/chat/stream",
}


def editor_page(request):
    """Always serve the React SPA. The React app handles empty state."""
    react_html = _STATIC_DIR / "index.html"
    if react_html.exists():
        return HttpResponse(react_html.read_text())
    return HttpResponse(
        _welcome_page("React build not found. Run: cd frontend && npm run build")
    )


@csrf_exempt
def api_dispatch(request, endpoint):
    """Dispatch API calls to handler functions."""
    editor = _get_editor(request)

    # Some endpoints require an editor
    _no_editor = endpoint in _NO_EDITOR_ENDPOINTS or endpoint.startswith(
        ("api/compose/export/", "api/gallery/thumbnail/", "api/file-content/")
    )
    if editor is None and not _no_editor:
        handler = HANDLERS.get(endpoint)
        if handler:
            return JsonResponse(
                {"error": "No recipe loaded. Select a file to begin."},
                status=400,
            )

    handler = HANDLERS.get(endpoint)
    if handler:
        try:
            return handler(request, editor)
        except Exception as e:
            logger.exception("[FigRecipe] API error on /%s", endpoint)
            return JsonResponse({"error": str(e)}, status=500)

    # Parameterized endpoints
    if endpoint.startswith("api/gallery/thumbnail/"):
        from .handlers import handle_gallery_thumbnail

        name = endpoint[len("api/gallery/thumbnail/") :]
        try:
            return handle_gallery_thumbnail(request, editor, name)
        except Exception as e:
            logger.exception("[FigRecipe] gallery thumbnail/%s", name)
            return JsonResponse({"error": str(e)}, status=500)

    if endpoint.startswith("call/"):
        if editor is None:
            return JsonResponse({"error": "No recipe loaded"}, status=400)
        call_id = endpoint[5:]
        try:
            return handle_single_call(request, editor, call_id)
        except Exception as e:
            logger.exception("[FigRecipe] API error on /call/%s", call_id)
            return JsonResponse({"error": str(e)}, status=500)

    if endpoint.startswith("download/"):
        if editor is None:
            return JsonResponse({"error": "No recipe loaded"}, status=400)
        fmt = endpoint[9:]
        try:
            return handle_download_fig(request, editor, fmt)
        except Exception as e:
            logger.exception("[FigRecipe] API error on /download/%s", fmt)
            return JsonResponse({"error": str(e)}, status=500)

    if endpoint.startswith("api/compose/export/"):
        from .handlers.compose import handle_compose_export

        fmt = endpoint[len("api/compose/export/") :]
        try:
            return handle_compose_export(request, editor, fmt)
        except Exception as e:
            logger.exception("[FigRecipe] compose export/%s", fmt)
            return JsonResponse({"error": str(e)}, status=500)

    if endpoint.startswith("api/file-content/"):
        from .handlers.files import handle_api_file_content

        file_path = endpoint[len("api/file-content/") :]
        try:
            return handle_api_file_content(request, editor, file_path)
        except Exception as e:
            logger.exception("[FigRecipe] file-content/%s", file_path)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": f"Unknown endpoint: {endpoint}"}, status=404)

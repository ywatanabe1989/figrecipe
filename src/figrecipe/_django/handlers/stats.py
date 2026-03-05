#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Statistical annotation handlers — add/remove/update/list brackets."""

import json
import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def handle_stats_add_bracket(request, editor):
    """Add a statistical significance bracket to the figure."""
    from figrecipe._annotations import add_stat_bracket
    from figrecipe._editor._helpers import render_with_overrides

    data = json.loads(request.body) if request.body else {}
    ax_index = data.get("ax_index", 0)
    x1 = data.get("x1")
    x2 = data.get("x2")
    p_value = data.get("p_value", 0.0)

    if x1 is None or x2 is None:
        return JsonResponse({"error": "Missing x1 or x2"}, status=400)

    try:
        fig = editor.fig
        axes_list = fig.get_axes()
        if ax_index >= len(axes_list):
            return JsonResponse(
                {"error": f"Invalid axis index: {ax_index}"}, status=400
            )

        ax = axes_list[ax_index]
        bracket_id = add_stat_bracket(
            ax,
            x1=x1,
            x2=x2,
            p_value=p_value,
            stars=data.get("stars", ""),
            y=data.get("y"),
            style=data.get("style", "bracket"),
            label=data.get("label", ""),
            effect_size=data.get("effect_size"),
            effect_size_name=data.get("effect_size_name"),
            bracket_id=data.get("bracket_id"),
        )

        img, bboxes, size = render_with_overrides(
            editor.fig, editor.get_effective_style(), editor.dark_mode
        )
        return JsonResponse(
            {
                "success": True,
                "bracket_id": bracket_id,
                "image": img,
                "bboxes": bboxes,
                "img_size": {"width": size[0], "height": size[1]},
            }
        )

    except Exception as e:
        logger.exception("[FigRecipe] stats/add_bracket failed")
        return JsonResponse({"error": str(e)}, status=500)


def handle_stats_remove_bracket(request, editor):
    """Remove a bracket by ID."""
    from figrecipe._annotations import remove_stat_bracket

    data = json.loads(request.body) if request.body else {}
    bracket_id = data.get("bracket_id")
    ax_index = data.get("ax_index", 0)

    if not bracket_id:
        return JsonResponse({"error": "Missing bracket_id"}, status=400)

    try:
        fig = editor.fig
        axes_list = fig.get_axes()
        if ax_index >= len(axes_list):
            return JsonResponse(
                {"error": f"Invalid axis index: {ax_index}"}, status=400
            )

        ax = axes_list[ax_index]
        removed = remove_stat_bracket(ax, bracket_id)

        if not removed:
            return JsonResponse(
                {"error": f"Bracket not found: {bracket_id}"}, status=404
            )

        from figrecipe._editor._helpers import render_with_overrides

        img, bboxes, size = render_with_overrides(
            editor.fig, editor.get_effective_style(), editor.dark_mode
        )
        return JsonResponse(
            {
                "success": True,
                "image": img,
                "bboxes": bboxes,
                "img_size": {"width": size[0], "height": size[1]},
            }
        )

    except Exception as e:
        logger.exception("[FigRecipe] stats/remove_bracket failed")
        return JsonResponse({"error": str(e)}, status=500)


def handle_stats_update_bracket(request, editor):
    """Update bracket properties (position, style, label)."""
    from figrecipe._annotations import update_stat_bracket

    data = json.loads(request.body) if request.body else {}
    bracket_id = data.get("bracket_id")
    ax_index = data.get("ax_index", 0)

    if not bracket_id:
        return JsonResponse({"error": "Missing bracket_id"}, status=400)

    try:
        fig = editor.fig
        axes_list = fig.get_axes()
        if ax_index >= len(axes_list):
            return JsonResponse(
                {"error": f"Invalid axis index: {ax_index}"}, status=400
            )

        ax = axes_list[ax_index]
        update_kwargs = {
            k: v for k, v in data.items() if k not in ("bracket_id", "ax_index")
        }
        updated = update_stat_bracket(ax, bracket_id, **update_kwargs)

        if not updated:
            return JsonResponse(
                {"error": f"Bracket not found: {bracket_id}"}, status=404
            )

        from figrecipe._editor._helpers import render_with_overrides

        img, bboxes, size = render_with_overrides(
            editor.fig, editor.get_effective_style(), editor.dark_mode
        )
        return JsonResponse(
            {
                "success": True,
                "image": img,
                "bboxes": bboxes,
                "img_size": {"width": size[0], "height": size[1]},
            }
        )

    except Exception as e:
        logger.exception("[FigRecipe] stats/update_bracket failed")
        return JsonResponse({"error": str(e)}, status=500)


def handle_stats_list_brackets(request, editor):
    """List all statistical brackets on the figure."""
    from figrecipe._annotations import list_stat_brackets

    ax_index = int(request.GET.get("ax_index", -1))

    try:
        fig = editor.fig
        axes_list = fig.get_axes()
        result = {}

        if ax_index >= 0:
            if ax_index >= len(axes_list):
                return JsonResponse(
                    {"error": f"Invalid axis index: {ax_index}"}, status=400
                )
            result[str(ax_index)] = list_stat_brackets(axes_list[ax_index])
        else:
            for i, ax in enumerate(axes_list):
                brackets = list_stat_brackets(ax)
                if brackets:
                    result[str(i)] = brackets

        return JsonResponse({"brackets": result})

    except Exception as e:
        logger.exception("[FigRecipe] stats/list_brackets failed")
        return JsonResponse({"error": str(e)}, status=500)

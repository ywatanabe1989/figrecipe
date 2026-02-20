#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for explicit MCP plot tools."""

from __future__ import annotations

__all__ = ["_build_result", "_create", "_parse_stats_results"]

from typing import Any, Dict, List, Optional


def _build_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "image_path": str(result["image_path"]) if result.get("image_path") else None,
        "recipe_path": str(result["recipe_path"])
        if result.get("recipe_path")
        else None,
        "success": True,
    }


def _parse_stats_results(
    stats_results: Optional[List[Dict[str, Any]]],
) -> Optional[List[Dict[str, Any]]]:
    """Convert scitex.stats result dicts to stat_annotations format.

    Accepts output from scitex.stats test functions (e.g. test_ttest_ind,
    test_anova) and converts to the figrecipe stat_annotations list format.

    Each scitex.stats result dict may contain:
        p_value  — float (required)
        x1, x2  — group positions (optional, inferred from order if absent)
        style    — "stars", "p_value", "both", "bracket_only" (optional)
        y        — bracket height (optional, auto-positioned if absent)
        text     — override annotation text (optional)

    Returns None if stats_results is None or empty.
    """
    if not stats_results:
        return None

    annotations = []
    for i, res in enumerate(stats_results):
        if not isinstance(res, dict):
            continue
        ann: Dict[str, Any] = {}

        # Extract p_value or pre-formatted text
        if "p_value" in res:
            ann["p_value"] = float(res["p_value"])
        elif "text" in res:
            ann["text"] = str(res["text"])
        else:
            continue  # Skip entries with no significance info

        # Group positions — explicit or inferred by order
        ann["x1"] = float(res.get("x1", i))
        ann["x2"] = float(res.get("x2", i + 1))

        if "y" in res:
            ann["y"] = float(res["y"])
        if "style" in res:
            ann["style"] = str(res["style"])

        annotations.append(ann)

    return annotations if annotations else None


def _create(
    plot_spec: Dict[str, Any],
    output_path: str,
    *,
    width_mm: float,
    height_mm: float,
    style: str,
    dpi: int,
    xlabel: Optional[str],
    ylabel: Optional[str],
    title: Optional[str],
    caption: Optional[str],
    legend: bool,
    xlim: Optional[List[float]],
    ylim: Optional[List[float]],
    stat_annotations: Optional[List[Dict[str, Any]]],
    stats_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a spec dict and delegate to create_figure_from_spec."""
    from ..._api._plot import create_figure_from_spec

    # Merge stats_results into stat_annotations (stats_results takes precedence)
    parsed = _parse_stats_results(stats_results)
    effective_annotations = parsed if parsed is not None else stat_annotations

    spec: Dict[str, Any] = {
        "figure": {"width_mm": width_mm, "height_mm": height_mm, "style": style},
        "plots": [plot_spec],
    }
    if xlabel is not None:
        spec["xlabel"] = xlabel
    if ylabel is not None:
        spec["ylabel"] = ylabel
    if title is not None:
        spec["title"] = title
    if caption is not None:
        spec["caption"] = caption
    if legend:
        spec["legend"] = legend
    if xlim is not None:
        spec["xlim"] = xlim
    if ylim is not None:
        spec["ylim"] = ylim
    if effective_annotations:
        spec["stat_annotations"] = effective_annotations

    result = create_figure_from_spec(
        spec=spec,
        output_path=output_path,
        dpi=dpi,
        save_recipe=True,
        show=False,
    )
    return _build_result(result)


# EOF

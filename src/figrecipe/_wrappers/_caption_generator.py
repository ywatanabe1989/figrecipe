#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caption generation utilities for scientific figures."""

from typing import Any, Dict, List, Literal, Optional

from ._stat_annotation import p_to_stars


def format_stats_value(value: float, precision: int = 2) -> str:
    """Format a statistical value for display."""
    if abs(value) >= 1000 or (abs(value) < 0.01 and value != 0):
        return f"{value:.{precision}e}"
    return f"{value:.{precision}f}"


def format_comparison(comp: Dict[str, Any], style: str = "publication") -> str:
    """Format a single comparison result.

    Parameters
    ----------
    comp : dict
        Comparison dict with keys like: name, p_value, stars, effect_size, method.
    style : str
        "publication", "brief", or "detailed".

    Returns
    -------
    str
        Formatted comparison string.
    """
    name = comp.get("name", "comparison")
    p_value = comp.get("p_value")
    stars = comp.get("stars") or (p_to_stars(p_value) if p_value else "")
    method = comp.get("method", "")
    effect_size = comp.get("effect_size")

    if style == "brief":
        if p_value is not None:
            return f"{name}: {stars}"
        return name

    elif style == "detailed":
        parts = [name]
        if method:
            parts.append(f"({method})")
        if p_value is not None:
            if p_value < 0.001:
                parts.append("p<0.001")
            else:
                parts.append(f"p={p_value:.3f}")
        if effect_size:
            if isinstance(effect_size, dict):
                es_name = effect_size.get("name", "d")
                es_val = effect_size.get("value", 0)
                parts.append(f"{es_name}={es_val:.2f}")
            else:
                parts.append(f"d={effect_size:.2f}")
        return " ".join(parts)

    else:  # publication
        if p_value is not None:
            if p_value < 0.001:
                p_str = "p<0.001"
            else:
                p_str = f"p={p_value:.3f}"
            if effect_size:
                if isinstance(effect_size, dict):
                    es_val = effect_size.get("value", 0)
                else:
                    es_val = effect_size
                return f"{name} ({p_str}, d={es_val:.2f})"
            return f"{name} ({p_str})"
        return name


def format_panel_stats(stats: Dict[str, Any], style: str = "publication") -> str:
    """Format panel-level statistics.

    Parameters
    ----------
    stats : dict
        Panel stats dict with keys like: n, mean, std, sem, group.
    style : str
        "publication", "brief", or "detailed".

    Returns
    -------
    str
        Formatted stats string.
    """
    parts = []

    group = stats.get("group")
    if group:
        parts.append(group)

    n = stats.get("n")
    if n is not None:
        parts.append(f"n={n}")

    mean = stats.get("mean")
    std = stats.get("std")
    sem = stats.get("sem")

    if mean is not None:
        if std is not None:
            parts.append(f"mean={format_stats_value(mean)}±{format_stats_value(std)}")
        elif sem is not None:
            parts.append(
                f"mean={format_stats_value(mean)}±{format_stats_value(sem)} SEM"
            )
        else:
            parts.append(f"mean={format_stats_value(mean)}")

    return ", ".join(parts) if parts else ""


def generate_figure_caption(
    title: Optional[str] = None,
    panel_captions: Optional[List[str]] = None,
    stats: Optional[Dict[str, Any]] = None,
    style: Literal["publication", "brief", "detailed"] = "publication",
    template: Optional[str] = None,
) -> str:
    """Generate a figure caption from components.

    Parameters
    ----------
    title : str, optional
        Figure title.
    panel_captions : list of str, optional
        List of panel captions.
    stats : dict, optional
        Figure-level stats with comparisons.
    style : str
        Caption style.
    template : str, optional
        Custom template with placeholders: {title}, {panels}, {stats}.

    Returns
    -------
    str
        Generated caption.
    """
    # Build components
    title_str = title or ""

    # Panel descriptions
    panels_str = ""
    if panel_captions:
        panels_str = " ".join(p for p in panel_captions if p)

    # Stats summary
    stats_str = ""
    if stats:
        comparisons = stats.get("comparisons", [])
        if comparisons:
            formatted = [format_comparison(c, style) for c in comparisons]
            stats_str = "; ".join(formatted)

    # Apply template
    if template:
        return template.format(
            title=title_str,
            panels=panels_str,
            stats=stats_str,
        ).strip()

    # Default formatting based on style
    parts = []
    if title_str:
        parts.append(title_str + ".")

    if panels_str:
        parts.append(panels_str)

    if stats_str:
        parts.append(stats_str + ".")

    return " ".join(parts).strip()


def generate_panel_caption(
    label: Optional[str] = None,
    stats: Optional[Dict[str, Any]] = None,
    style: Literal["publication", "brief", "detailed"] = "publication",
) -> str:
    """Generate a panel caption from stats.

    Parameters
    ----------
    label : str, optional
        Panel label like "A" or "(A)".
    stats : dict, optional
        Panel-level stats.
    style : str
        Caption style.

    Returns
    -------
    str
        Generated panel caption.
    """
    parts = []

    if label:
        # Ensure label is in parentheses
        if not label.startswith("("):
            label = f"({label})"
        parts.append(label)

    if stats:
        stats_str = format_panel_stats(stats, style)
        if stats_str:
            parts.append(stats_str)

    return " ".join(parts)

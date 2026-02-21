#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Axes decoration helpers for declarative plot creation."""

from typing import Any, Dict, List


def apply_decorations(ax, spec: Dict[str, Any]) -> None:
    """Apply axes decorations (labels, title, legend, etc.)."""
    if "xlabel" in spec:
        ax.set_xlabel(spec["xlabel"])
    if "ylabel" in spec:
        ax.set_ylabel(spec["ylabel"])
    if "title" in spec:
        ax.set_title(spec["title"])
    if "xlim" in spec:
        ax.set_xlim(spec["xlim"])
    if "ylim" in spec:
        ax.set_ylim(spec["ylim"])

    _apply_tick_customization(ax, spec)

    if spec.get("legend"):
        ax.legend()
    if spec.get("grid"):
        ax.grid(True)
    if "aspect" in spec:
        ax.set_aspect(spec["aspect"])
    if "xscale" in spec:
        ax.set_xscale(spec["xscale"])
    if "yscale" in spec:
        ax.set_yscale(spec["yscale"])

    if "stat_annotations" in spec:
        apply_stat_annotations(ax, spec["stat_annotations"])

    if "annotations" in spec:
        apply_text_annotations(ax, spec["annotations"])


def _apply_tick_customization(ax, spec: Dict[str, Any]) -> None:
    """Apply custom tick positions and labels."""
    underlying_ax = ax._ax if hasattr(ax, "_ax") else ax

    if "xticks" in spec:
        xticks_spec = spec["xticks"]
        if isinstance(xticks_spec, dict):
            positions = xticks_spec.get("positions")
            labels = xticks_spec.get("labels")
            if positions is not None:
                underlying_ax.set_xticks(positions)
            if labels is not None:
                underlying_ax.set_xticklabels(labels)
        elif isinstance(xticks_spec, list):
            underlying_ax.set_xticks(xticks_spec)

    if "yticks" in spec:
        yticks_spec = spec["yticks"]
        if isinstance(yticks_spec, dict):
            positions = yticks_spec.get("positions")
            labels = yticks_spec.get("labels")
            if positions is not None:
                underlying_ax.set_yticks(positions)
            if labels is not None:
                underlying_ax.set_yticklabels(labels)
        elif isinstance(yticks_spec, list):
            underlying_ax.set_yticks(yticks_spec)


def apply_stat_annotations(ax, annotations: List[Dict[str, Any]]) -> None:
    """Apply statistical significance annotations."""
    from .._wrappers._stat_annotation import draw_stat_annotation

    underlying_ax = ax._ax if hasattr(ax, "_ax") else ax

    for ann in annotations:
        x1 = ann.get("x1", 0)
        x2 = ann.get("x2", 1)
        y = ann.get("y")
        text = ann.get("text")
        p_value = ann.get("p_value")
        style = ann.get("style", "stars")

        draw_stat_annotation(
            underlying_ax,
            x1=x1,
            x2=x2,
            y=y,
            text=text,
            p_value=p_value,
            style=style,
        )


def apply_text_annotations(ax, annotations: List[Dict[str, Any]]) -> None:
    """Apply text annotations to axes."""
    underlying_ax = ax._ax if hasattr(ax, "_ax") else ax

    for ann in annotations:
        text = ann.get("text", "")
        xy = ann.get("xy", (0.5, 0.5))
        fontsize = ann.get("fontsize", 8)
        ha = ann.get("ha", "center")
        va = ann.get("va", "center")
        color = ann.get("color", "black")
        fontweight = ann.get("fontweight", "normal")

        underlying_ax.text(
            xy[0],
            xy[1],
            text,
            fontsize=fontsize,
            ha=ha,
            va=va,
            color=color,
            fontweight=fontweight,
        )


# EOF

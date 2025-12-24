#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Violin plot replay for figure reproduction."""

from typing import Any, Dict

import numpy as np
from matplotlib.axes import Axes

from .._recorder import CallRecord


def replay_violinplot_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a violinplot call with inner option support.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The violinplot call to replay.

    Returns
    -------
    Any
        Result of the violinplot call.
    """
    # Import from _core module (will be available after full package setup)
    from ._core import _reconstruct_kwargs, _reconstruct_value

    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        args.append(value)

    # Get kwargs and reconstruct arrays
    kwargs = _reconstruct_kwargs(call.kwargs)

    # Extract inner option (not a matplotlib kwarg)
    inner = kwargs.pop("inner", "box")

    # Get display options
    showmeans = kwargs.pop("showmeans", False)
    showmedians = kwargs.pop("showmedians", True)
    showextrema = kwargs.pop("showextrema", False)

    # When using inner box/swarm, suppress default median/extrema lines
    if inner in ("box", "swarm"):
        showmedians = False
        showextrema = False

    # Call matplotlib's violinplot
    try:
        result = ax.violinplot(
            *args,
            showmeans=showmeans,
            showmedians=showmedians,
            showextrema=showextrema,
            **kwargs,
        )

        # Get style settings for inner display
        from ..styles import get_style

        style = get_style()
        violin_style = style.get("violinplot", {}) if style else {}

        # Apply alpha from style to violin bodies
        alpha = violin_style.get("alpha", 0.7)
        if "bodies" in result:
            for body in result["bodies"]:
                body.set_alpha(alpha)

        # Determine positions
        dataset = args[0] if args else []
        positions = kwargs.get("positions")
        if positions is None:
            positions = list(range(1, len(dataset) + 1))

        # Overlay inner elements based on inner type
        if inner == "box":
            _add_violin_inner_box(ax, dataset, positions, violin_style)
        elif inner == "swarm":
            _add_violin_inner_swarm(ax, dataset, positions, violin_style)
        elif inner == "stick":
            _add_violin_inner_stick(ax, dataset, positions, violin_style)
        elif inner == "point":
            _add_violin_inner_point(ax, dataset, positions, violin_style)

        return result
    except Exception as e:
        import warnings

        warnings.warn(f"Failed to replay violinplot: {e}")
        return None


def _add_violin_inner_box(ax: Axes, dataset, positions, style: Dict[str, Any]) -> None:
    """Add box plot inside violin for reproduction."""
    from ..styles._style_applier import mm_to_pt

    whisker_lw = mm_to_pt(style.get("whisker_mm", 0.2))
    median_size = mm_to_pt(style.get("median_mm", 0.8))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        q1, median, q3 = np.percentile(data, [25, 50, 75])
        iqr = q3 - q1
        whisker_low = max(data.min(), q1 - 1.5 * iqr)
        whisker_high = min(data.max(), q3 + 1.5 * iqr)

        # Draw box (Q1 to Q3)
        ax.vlines(pos, q1, q3, colors="black", linewidths=whisker_lw, zorder=3)
        # Draw whiskers
        ax.vlines(
            pos, whisker_low, q1, colors="black", linewidths=whisker_lw * 0.5, zorder=3
        )
        ax.vlines(
            pos, q3, whisker_high, colors="black", linewidths=whisker_lw * 0.5, zorder=3
        )
        # Draw median as a white dot with black edge
        ax.scatter(
            [pos],
            [median],
            s=median_size**2,
            c="white",
            edgecolors="black",
            linewidths=whisker_lw,
            zorder=4,
        )


def _add_violin_inner_swarm(
    ax: Axes, dataset, positions, style: Dict[str, Any]
) -> None:
    """Add swarm points inside violin for reproduction."""
    from ..styles._style_applier import mm_to_pt

    point_size = mm_to_pt(style.get("median_mm", 0.8))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        n = len(data)
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, n)
        x_positions = pos + jitter
        ax.scatter(x_positions, data, s=point_size**2, c="black", alpha=0.5, zorder=3)


def _add_violin_inner_stick(
    ax: Axes, dataset, positions, style: Dict[str, Any]
) -> None:
    """Add stick markers inside violin for reproduction."""
    from ..styles._style_applier import mm_to_pt

    lw = mm_to_pt(style.get("whisker_mm", 0.2))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        for val in data:
            ax.hlines(
                val,
                pos - 0.05,
                pos + 0.05,
                colors="black",
                linewidths=lw * 0.5,
                alpha=0.3,
                zorder=3,
            )


def _add_violin_inner_point(
    ax: Axes, dataset, positions, style: Dict[str, Any]
) -> None:
    """Add point markers inside violin for reproduction."""
    from ..styles._style_applier import mm_to_pt

    point_size = mm_to_pt(style.get("median_mm", 0.8)) * 0.5

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        x_positions = np.full_like(data, pos)
        ax.scatter(x_positions, data, s=point_size**2, c="black", alpha=0.3, zorder=3)


__all__ = ["replay_violinplot_call"]

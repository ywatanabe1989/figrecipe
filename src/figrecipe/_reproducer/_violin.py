#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Violin plot replay for figure reproduction."""

from typing import Any

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
    from ._reconstruct import reconstruct_kwargs, reconstruct_value

    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = reconstruct_value(arg_data)
        args.append(value)

    # Get kwargs and reconstruct arrays
    kwargs = reconstruct_kwargs(call.kwargs)

    # Extract inner option (not a matplotlib kwarg)
    inner = kwargs.pop("inner", None)

    # Extract body colors and alphas if recorded
    body_colors = kwargs.pop("_body_colors", None)
    body_alphas = kwargs.pop("_body_alphas", None)

    # Get display options - use matplotlib defaults (False) if not recorded
    showmeans = kwargs.pop("showmeans", False)
    showmedians = kwargs.pop("showmedians", False)
    showextrema = kwargs.pop("showextrema", False)

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
        from ..styles._internal import get_style

        style = get_style()
        violin_style = style.get("violinplot", {}) if style else {}

        # Apply colors and alpha to violin bodies
        if "bodies" in result:
            for i, body in enumerate(result["bodies"]):
                # Use recorded colors if available, otherwise use style palette
                if body_colors is not None and i < len(body_colors):
                    body.set_facecolor(body_colors[i])
                # Use recorded alphas if available, otherwise use style default
                if (
                    body_alphas is not None
                    and i < len(body_alphas)
                    and body_alphas[i] is not None
                ):
                    body.set_alpha(body_alphas[i])
                else:
                    body.set_alpha(violin_style.get("alpha", 0.7))

        # Determine positions
        dataset = args[0] if args else []
        positions = kwargs.get("positions")
        if positions is None:
            positions = list(range(1, len(dataset) + 1))

        # Overlay inner elements based on inner type
        # Use the same helper functions as original to ensure pixel-perfect match
        from .._wrappers._violin_helpers import (
            add_violin_inner_box,
            add_violin_inner_point,
            add_violin_inner_stick,
            add_violin_inner_swarm,
        )

        if inner == "box":
            add_violin_inner_box(ax, dataset, positions, violin_style)
        elif inner == "swarm":
            add_violin_inner_swarm(ax, dataset, positions, violin_style)
        elif inner == "stick":
            add_violin_inner_stick(ax, dataset, positions, violin_style)
        elif inner == "point":
            add_violin_inner_point(ax, dataset, positions, violin_style)

        return result
    except Exception as e:
        import warnings

        warnings.warn(f"Failed to replay violinplot: {e}")
        return None


__all__ = ["replay_violinplot_call"]

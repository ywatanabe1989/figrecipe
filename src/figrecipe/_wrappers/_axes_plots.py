#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom plotting methods for RecordingAxes."""

from typing import TYPE_CHECKING, Any, List, Optional

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .._recorder import Recorder


def pie_plot(
    ax: "Axes",
    x,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    **kwargs,
) -> tuple:
    """Pie chart with automatic SCITEX styling."""
    from ..styles import get_style

    # Get style settings before calling pie
    style = get_style()
    pie_style = style.get("pie", {}) if style else {}

    # Apply wedge edge styling via wedgeprops if not already specified
    kwargs = _apply_pie_wedgeprops(kwargs, pie_style)

    # Call matplotlib's pie
    result = ax.pie(x, **kwargs)

    # Apply additional style settings
    if style:
        _apply_pie_text_style(ax, pie_style, style)
        _apply_pie_axes_visibility(ax, pie_style)

    # Record the call if tracking is enabled
    if track:
        recorder.record_call(
            ax_position=position,
            method_name="pie",
            args=(x,),
            kwargs=kwargs,
            call_id=call_id,
        )

    return result


def _apply_pie_wedgeprops(kwargs: dict, pie_style: dict) -> dict:
    """Apply wedge properties to pie kwargs."""
    from .._utils._units import mm_to_pt

    edge_color = pie_style.get("edge_color", "black")
    edge_mm = pie_style.get("edge_mm", 0.2)
    edge_lw = mm_to_pt(edge_mm)

    if "wedgeprops" not in kwargs:
        kwargs["wedgeprops"] = {"edgecolor": edge_color, "linewidth": edge_lw}
    elif "edgecolor" not in kwargs.get("wedgeprops", {}):
        kwargs["wedgeprops"]["edgecolor"] = edge_color
        kwargs["wedgeprops"]["linewidth"] = edge_lw

    return kwargs


def _apply_pie_text_style(ax: "Axes", pie_style: dict, style) -> None:
    """Apply text styling to pie chart."""
    from ..styles._style_applier import check_font

    text_pt = pie_style.get("text_pt", 6)
    font_family = check_font(style.get("fonts", {}).get("family", "Arial"))

    # Get text color from rcParams for dark mode support
    import matplotlib.pyplot as mpl_plt

    text_color = mpl_plt.rcParams.get("text.color", "black")

    for text in ax.texts:
        text.set_fontsize(text_pt)
        text.set_fontfamily(font_family)
        text.set_color(text_color)


def _apply_pie_axes_visibility(ax: "Axes", pie_style: dict) -> None:
    """Apply axes visibility settings for pie chart."""
    show_axes = pie_style.get("show_axes", False)
    if not show_axes:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        for spine in ax.spines.values():
            spine.set_visible(False)


def imshow_plot(
    ax: "Axes",
    X,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    **kwargs,
):
    """Display image with automatic SCITEX styling."""
    from ..styles import get_style

    # Call matplotlib's imshow
    result = ax.imshow(X, **kwargs)

    # Get style settings
    style = get_style()
    if style:
        imshow_style = style.get("imshow", {})
        show_axes = imshow_style.get("show_axes", True)
        show_labels = imshow_style.get("show_labels", True)

        if not show_axes:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            for spine in ax.spines.values():
                spine.set_visible(False)

        if not show_labels:
            ax.set_xlabel("")
            ax.set_ylabel("")

    # Record the call if tracking is enabled
    if track:
        recorder.record_call(
            ax_position=position,
            method_name="imshow",
            args=(X,),
            kwargs=kwargs,
            call_id=call_id,
        )

    return result


def violinplot_plot(
    ax: "Axes",
    dataset,
    positions,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    inner: Optional[str],
    **kwargs,
) -> dict:
    """Violin plot with support for inner display options."""
    from ..styles import get_style

    # Get style settings
    style = get_style()
    violin_style = style.get("violinplot", {}) if style else {}

    # Determine inner type
    if inner is None:
        inner = violin_style.get("inner", "box")

    # Get violin display options from style
    showmeans = kwargs.pop("showmeans", violin_style.get("showmeans", False))
    showmedians = kwargs.pop("showmedians", violin_style.get("showmedians", True))
    showextrema = kwargs.pop("showextrema", violin_style.get("showextrema", False))

    # Call matplotlib's violinplot
    result = ax.violinplot(
        dataset,
        positions=positions,
        showmeans=showmeans,
        showmedians=showmedians if inner not in ("box", "swarm") else False,
        showextrema=showextrema if inner not in ("box", "swarm") else False,
        **kwargs,
    )

    # Apply alpha from style to violin bodies
    alpha = violin_style.get("alpha", 0.7)
    if "bodies" in result:
        for body in result["bodies"]:
            body.set_alpha(alpha)

    # Overlay inner elements
    if positions is None:
        positions = list(range(1, len(dataset) + 1))

    _add_violin_inner_elements(ax, dataset, positions, inner, violin_style)

    # Record the call if tracking is enabled
    if track:
        recorded_kwargs = kwargs.copy()
        recorded_kwargs["inner"] = inner
        recorded_kwargs["showmeans"] = showmeans
        recorded_kwargs["showmedians"] = showmedians
        recorded_kwargs["showextrema"] = showextrema

        recorder.record_call(
            ax_position=position,
            method_name="violinplot",
            args=(dataset,),
            kwargs=recorded_kwargs,
            call_id=call_id,
        )

    return result


def _add_violin_inner_elements(
    ax: "Axes", dataset, positions, inner: str, violin_style: dict
) -> None:
    """Add inner elements to violin plot."""
    from ._violin_helpers import (
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


def joyplot_plot(
    ax: "Axes",
    recording_axes,
    arrays,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    overlap: float,
    fill_alpha: float,
    line_alpha: float,
    colors,
    labels,
    **kwargs,
):
    """Create a joyplot (ridgeline plot)."""
    from .._utils._units import mm_to_pt
    from ..styles import get_style

    # Convert dict to list of arrays
    if isinstance(arrays, dict):
        if labels is None:
            labels = list(arrays.keys())
        arrays = list(arrays.values())

    n_ridges = len(arrays)

    from ._plot_helpers import compute_joyplot_kdes, get_colors_from_style

    # Get colors from style or use default cycle
    colors = get_colors_from_style(n_ridges, colors)

    # Calculate global x range
    all_data = np.concatenate([np.asarray(arr) for arr in arrays])
    x_min, x_max = np.min(all_data), np.max(all_data)
    x_range = x_max - x_min
    x_padding = x_range * 0.1
    x = np.linspace(x_min - x_padding, x_max + x_padding, 200)

    # Calculate KDEs
    kdes, max_density = compute_joyplot_kdes(arrays, x)

    # Scale factor for ridge height
    ridge_height = 1.0 / (1.0 - overlap * 0.5) if overlap < 1 else 2.0

    # Get line width from style
    style = get_style()
    lw = mm_to_pt(0.2)
    if style and "lines" in style:
        lw = mm_to_pt(style.lines.get("trace_mm", 0.2))

    # Plot each ridge from back to front
    for i in range(n_ridges - 1, -1, -1):
        color = colors[i % len(colors)]
        baseline = i * (1.0 - overlap)
        scaled_density = (
            kdes[i] / max_density * ridge_height if max_density > 0 else kdes[i]
        )

        ax.fill_between(
            x,
            baseline,
            baseline + scaled_density,
            facecolor=color,
            edgecolor="none",
            alpha=fill_alpha,
        )
        ax.plot(
            x,
            baseline + scaled_density,
            color=color,
            alpha=line_alpha,
            linewidth=lw,
        )

    # Set y limits
    ax.set_ylim(-0.1, n_ridges * (1.0 - overlap) + ridge_height)

    # Set y-axis labels
    if labels:
        y_positions = [(i * (1.0 - overlap)) + 0.3 for i in range(n_ridges)]
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels)
    else:
        ax.set_yticks([])

    # Record the call if tracking is enabled
    if track:
        recorder.record_call(
            ax_position=position,
            method_name="joyplot",
            args=(arrays,),
            kwargs={
                "overlap": overlap,
                "fill_alpha": fill_alpha,
                "line_alpha": line_alpha,
                "labels": labels,
            },
            call_id=call_id,
        )

    return recording_axes


def swarmplot_plot(
    ax: "Axes",
    data,
    positions,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    size: Optional[float],
    color,
    alpha: float,
    jitter: float,
    **kwargs,
) -> List[Any]:
    """Create a swarm plot (beeswarm plot)."""
    from .._utils._units import mm_to_pt
    from ..styles import get_style

    # Get style
    style = get_style()

    # Default marker size from style
    if size is None:
        if style and "markers" in style:
            size = style.markers.get("scatter_mm", 0.8)
        else:
            size = 0.8
    size_pt = mm_to_pt(size) ** 2

    from ._plot_helpers import beeswarm_positions, get_colors_from_style

    # Get colors
    colors = get_colors_from_style(len(data), color)

    # Default positions
    if positions is None:
        positions = list(range(1, len(data) + 1))

    # Random generator for reproducible jitter
    rng = np.random.default_rng(42)

    results = []
    for i, (arr, pos) in enumerate(zip(data, positions)):
        arr = np.asarray(arr)
        x_jitter = beeswarm_positions(arr, jitter, rng)
        x_positions = pos + x_jitter
        c = colors[i % len(colors)]
        result = ax.scatter(x_positions, arr, s=size_pt, c=[c], alpha=alpha, **kwargs)
        results.append(result)

    # Record the call if tracking is enabled
    if track:
        recorder.record_call(
            ax_position=position,
            method_name="swarmplot",
            args=(data,),
            kwargs={
                "positions": positions,
                "size": size,
                "alpha": alpha,
                "jitter": jitter,
            },
            call_id=call_id,
        )

    return results


__all__ = [
    "pie_plot",
    "imshow_plot",
    "violinplot_plot",
    "joyplot_plot",
    "swarmplot_plot",
]

# EOF

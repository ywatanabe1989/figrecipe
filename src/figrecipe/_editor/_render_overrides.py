#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style override application for preview rendering."""

from typing import Any, Dict, List, Optional

from matplotlib.axes import Axes
from matplotlib.figure import Figure


def apply_overrides(
    fig: Figure, overrides: Dict[str, Any], record: Optional[Any] = None
) -> None:
    """
    Apply style overrides to figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure.
    overrides : dict
        Style overrides with keys like:
        - axes_width_mm, axes_height_mm
        - fonts_axis_label_pt, fonts_tick_label_pt
        - lines_trace_mm
        - spacing_horizontal_mm, spacing_vertical_mm
        - margins_left_mm, margins_right_mm, margins_bottom_mm, margins_top_mm
        - call_overrides: dict mapping call_id -> {param: value}
        - etc.
    record : FigureRecord, optional
        Recording record to access call IDs for grouping elements.
    """
    from ..styles._style_applier import apply_style_mm
    from ._figure_layout import apply_figure_layout_overrides

    # Apply figure-level layout overrides (spacing, margins)
    apply_figure_layout_overrides(fig, overrides, record)

    axes_list = fig.get_axes()

    for ax in axes_list:
        # Apply mm-based styling
        apply_style_mm(ax, overrides)

        # Apply specific overrides that aren't handled by apply_style_mm
        _apply_font_overrides(ax, overrides)
        _apply_tick_overrides(ax, overrides)
        _apply_behavior_overrides(ax, overrides)
        _apply_legend_overrides(ax, overrides)
        _apply_line_overrides(ax, overrides)
        _apply_marker_overrides(ax, overrides)

        # Apply color palette to existing elements
        color_palette = overrides.get("color_palette")
        if color_palette is not None:
            ax_record = _find_ax_record(ax, axes_list, record)
            apply_color_palette(ax, color_palette, ax_record)

    # Apply call-specific overrides (from Element tab edits)
    # Single source of truth - same function for initial and re-render
    call_overrides = overrides.get("call_overrides", {})
    if call_overrides and record:
        from ._call_overrides import apply_call_overrides

        apply_call_overrides(fig, call_overrides, record)


def _apply_font_overrides(ax: Axes, overrides: Dict[str, Any]) -> None:
    """Apply font-related overrides to axes."""
    # Font sizes (YAML: fonts_axis_label_pt, legacy: axis_font_size_pt)
    axis_fs = overrides.get("fonts_axis_label_pt", overrides.get("axis_font_size_pt"))
    if axis_fs is not None:
        ax.xaxis.label.set_fontsize(axis_fs)
        ax.yaxis.label.set_fontsize(axis_fs)

    tick_fs = overrides.get("fonts_tick_label_pt", overrides.get("tick_font_size_pt"))
    if tick_fs is not None:
        ax.tick_params(labelsize=tick_fs)

    title_fs = overrides.get("fonts_title_pt", overrides.get("title_font_size_pt"))
    if title_fs is not None:
        ax.title.set_fontsize(title_fs)

    family = overrides.get("fonts_family", overrides.get("font_family"))
    if family is not None:
        ax.xaxis.label.set_fontfamily(family)
        ax.yaxis.label.set_fontfamily(family)
        ax.title.set_fontfamily(family)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontfamily(family)


def _apply_tick_overrides(ax: Axes, overrides: Dict[str, Any]) -> None:
    """Apply tick-related overrides to axes."""
    # Ticks (YAML: ticks_direction, legacy: tick_direction)
    tick_dir = overrides.get("ticks_direction", overrides.get("tick_direction"))
    if tick_dir is not None and tick_dir in ("in", "out", "inout"):
        ax.tick_params(direction=tick_dir)

    tick_len = overrides.get("ticks_length_mm", overrides.get("tick_length_mm"))
    if tick_len is not None:
        from .._utils._units import mm_to_pt

        length = mm_to_pt(tick_len)
        ax.tick_params(length=length)


def _apply_behavior_overrides(ax: Axes, overrides: Dict[str, Any]) -> None:
    """Apply behavior-related overrides (grid, spines)."""
    # Grid (YAML: behavior_grid, legacy: grid)
    grid_value = overrides.get("behavior_grid", overrides.get("grid"))
    if grid_value is not None:
        if grid_value:
            ax.grid(True, alpha=0.3)
        else:
            ax.grid(False)

    # Spines (YAML: behavior_hide_top_spine, legacy: hide_top_spine)
    hide_top = overrides.get("behavior_hide_top_spine", overrides.get("hide_top_spine"))
    if hide_top is not None:
        ax.spines["top"].set_visible(not hide_top)

    hide_right = overrides.get(
        "behavior_hide_right_spine", overrides.get("hide_right_spine")
    )
    if hide_right is not None:
        ax.spines["right"].set_visible(not hide_right)


def _apply_legend_overrides(ax: Axes, overrides: Dict[str, Any]) -> None:
    """Apply legend-related overrides."""
    legend = ax.get_legend()
    if legend is not None:
        if "legend_frameon" in overrides:
            legend.set_frame_on(overrides["legend_frameon"])

        if "legend_alpha" in overrides:
            frame = legend.get_frame()
            fc = frame.get_facecolor()
            frame.set_facecolor((*fc[:3], overrides["legend_alpha"]))


def _apply_line_overrides(ax: Axes, overrides: Dict[str, Any]) -> None:
    """Apply line-related overrides."""
    # Line widths (YAML: lines_trace_mm, legacy: trace_thickness_mm)
    trace_mm = overrides.get("lines_trace_mm", overrides.get("trace_thickness_mm"))
    if trace_mm is not None:
        from .._utils._units import mm_to_pt

        lw = mm_to_pt(trace_mm)
        for line in ax.get_lines():
            line.set_linewidth(lw)


def _apply_marker_overrides(ax: Axes, overrides: Dict[str, Any]) -> None:
    """Apply marker-related overrides."""
    # Marker sizes (YAML: markers_scatter_mm, legacy: marker_size_mm)
    # Only apply to PathCollection (scatter), not PolyCollection (violin/fill)
    scatter_mm = overrides.get(
        "markers_scatter_mm",
        overrides.get("markers_size_mm", overrides.get("marker_size_mm")),
    )
    if scatter_mm is not None:
        from matplotlib.collections import PathCollection

        from .._utils._units import mm_to_scatter_size

        size = mm_to_scatter_size(scatter_mm)
        for coll in ax.collections:
            # Only apply to scatter plots (PathCollection), not violin/fill (PolyCollection)
            if isinstance(coll, PathCollection):
                try:
                    coll.set_sizes([size])
                except Exception:
                    pass


def _find_ax_record(ax: Axes, axes_list: List[Axes], record: Optional[Any]) -> Any:
    """Find the AxesRecord for a given axes."""
    if record is None or not hasattr(record, "axes"):
        return None

    # Find ax position in the figure's axes list
    ax_idx = axes_list.index(ax)
    # AxesRecord keys are position tuples like "(0, 0)", "(0, 1)", etc.
    # Try to match by index order
    ax_keys = sorted(record.axes.keys())
    if ax_idx < len(ax_keys):
        return record.axes.get(ax_keys[ax_idx])
    return None


def apply_color_palette(
    ax: Axes, color_palette: List[Any], ax_record: Optional[Any] = None
) -> None:
    """
    Apply color palette to existing plot elements, grouping by call_id.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes containing plot elements.
    color_palette : list
        List of colors (RGB tuples or color names).
    ax_record : AxesRecord, optional
        Record of calls for this axes (for grouping elements by call_id).
    """

    # Normalize colors (RGB 0-255 to 0-1)
    normalized_palette = _normalize_color_palette(color_palette)
    if not normalized_palette:
        return

    # Build call_id to color index mapping from record
    call_color_map = _build_call_color_map(ax_record)

    # Apply to different element types
    _apply_colors_to_lines(ax, normalized_palette, ax_record, call_color_map)
    _apply_colors_to_bars(ax, normalized_palette, ax_record, call_color_map)
    _apply_colors_to_pie(ax, normalized_palette, ax_record)
    _apply_colors_to_scatter(ax, normalized_palette, ax_record, call_color_map)
    _apply_colors_to_poly(ax, normalized_palette)
    _update_legend_colors(ax, normalized_palette)


def _normalize_color_palette(color_palette: List[Any]) -> List[Any]:
    """Normalize color palette to 0-1 range."""
    normalized = []
    for c in color_palette:
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            if all(v <= 1.0 for v in c):
                normalized.append(tuple(c))
            else:
                normalized.append(tuple(v / 255.0 for v in c))
        else:
            normalized.append(c)
    return normalized


def _build_call_color_map(ax_record: Optional[Any]) -> Dict[str, int]:
    """Build mapping from call_id to color index."""
    call_color_map = {}
    if ax_record:
        color_idx = 0
        for call in ax_record.calls:
            if call.function in (
                "plot",
                "scatter",
                "bar",
                "barh",
                "hist",
                "pie",
                "fill",
                "fill_between",
                "fill_betweenx",
            ):
                if call.id not in call_color_map:
                    call_color_map[call.id] = color_idx
                    color_idx += 1
    return call_color_map


def _apply_colors_to_lines(
    ax: Axes,
    palette: List[Any],
    ax_record: Optional[Any],
    call_color_map: Dict[str, int],
) -> None:
    """Apply colors to line elements."""
    lines = ax.get_lines()
    line_calls = [
        c for c in (ax_record.calls if ax_record else []) if c.function == "plot"
    ]
    for i, line in enumerate(lines):
        # Skip internal lines (boxplot whiskers, etc.)
        label = line.get_label()
        if label.startswith("_"):
            continue
        if i < len(line_calls) and line_calls[i].id in call_color_map:
            color_idx = call_color_map[line_calls[i].id]
        else:
            color_idx = i
        line.set_color(palette[color_idx % len(palette)])


def _apply_colors_to_bars(
    ax: Axes,
    palette: List[Any],
    ax_record: Optional[Any],
    call_color_map: Dict[str, int],
) -> None:
    """Apply colors to bar and histogram elements.

    Skips bars that have an explicit 'color' kwarg set (from Element tab edits).
    """
    from matplotlib.patches import Rectangle

    rectangles = [p for p in ax.patches if isinstance(p, Rectangle)]
    if not rectangles:
        return

    bar_calls = [
        c
        for c in (ax_record.calls if ax_record else [])
        if c.function in ("bar", "barh", "hist")
    ]
    if bar_calls:
        rect_per_call = len(rectangles) // len(bar_calls) if bar_calls else 1
        for i, patch in enumerate(rectangles):
            call_idx = (
                min(i // rect_per_call, len(bar_calls) - 1) if rect_per_call > 0 else 0
            )
            # Skip if this call has an explicit color set (user override)
            if call_idx < len(bar_calls) and "color" in bar_calls[call_idx].kwargs:
                continue
            if call_idx < len(bar_calls) and bar_calls[call_idx].id in call_color_map:
                color_idx = call_color_map[bar_calls[call_idx].id]
            else:
                color_idx = call_idx
            patch.set_facecolor(palette[color_idx % len(palette)])
    else:
        # No record, apply single color to all bars
        color = palette[0]
        for patch in rectangles:
            patch.set_facecolor(color)


def _apply_colors_to_pie(
    ax: Axes, palette: List[Any], ax_record: Optional[Any] = None
) -> None:
    """Apply colors to pie chart wedges.

    If the pie call has custom colors in kwargs, those are used.
    Otherwise, the theme palette is applied.
    """
    from matplotlib.patches import Wedge

    wedges = [p for p in ax.patches if isinstance(p, Wedge)]
    if not wedges:
        return

    # Check if pie call has custom colors
    custom_colors = None
    if ax_record:
        for call in ax_record.calls:
            if call.function == "pie" and "colors" in call.kwargs:
                custom_colors = call.kwargs["colors"]
                break

    # Use custom colors if available, otherwise use palette
    if custom_colors and isinstance(custom_colors, list):
        # Normalize custom colors
        colors_to_use = []
        for c in custom_colors:
            if isinstance(c, str):
                colors_to_use.append(c)
            elif isinstance(c, (list, tuple)) and len(c) >= 3:
                if all(v <= 1.0 for v in c):
                    colors_to_use.append(tuple(c))
                else:
                    colors_to_use.append(tuple(v / 255.0 for v in c))
            else:
                colors_to_use.append(c)
    else:
        colors_to_use = palette

    for i, wedge in enumerate(wedges):
        color = colors_to_use[i % len(colors_to_use)]
        wedge.set_facecolor(color)
        wedge.set_edgecolor("black")


def _apply_colors_to_scatter(
    ax: Axes,
    palette: List[Any],
    ax_record: Optional[Any],
    call_color_map: Dict[str, int],
) -> None:
    """Apply colors to scatter plot collections."""
    from matplotlib.collections import PathCollection

    scatter_collections = [c for c in ax.collections if isinstance(c, PathCollection)]
    scatter_calls = [
        c for c in (ax_record.calls if ax_record else []) if c.function == "scatter"
    ]
    for i, coll in enumerate(scatter_collections):
        if i < len(scatter_calls) and scatter_calls[i].id in call_color_map:
            color_idx = call_color_map[scatter_calls[i].id]
        else:
            color_idx = i
        coll.set_facecolor(palette[color_idx % len(palette)])


def _apply_colors_to_poly(ax: Axes, palette: List[Any]) -> None:
    """Apply colors to polygon collections (violin, fill)."""
    from matplotlib.collections import PolyCollection

    poly_collections = [c for c in ax.collections if isinstance(c, PolyCollection)]
    for i, coll in enumerate(poly_collections):
        color = palette[i % len(palette)]
        coll.set_facecolor(color)


def _update_legend_colors(ax: Axes, palette: List[Any]) -> None:
    """Update legend colors to reflect new palette."""
    legend = ax.get_legend()
    if legend is None:
        return

    handles = (
        legend.legend_handles
        if hasattr(legend, "legend_handles")
        else legend.legendHandles
    )
    for i, handle in enumerate(handles):
        if i < len(palette):
            color = palette[i % len(palette)]
            if hasattr(handle, "set_color"):
                handle.set_color(color)
            elif hasattr(handle, "set_facecolor"):
                handle.set_facecolor(color)


def apply_dark_mode(fig: Figure) -> None:
    """
    Apply dark mode colors to figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure.
    """
    # Dark theme colors
    bg_color = "#1a1a1a"
    text_color = "#e8e8e8"

    # Update rcParams for dark mode (pie charts, panel labels)
    import matplotlib as mpl

    mpl.rcParams["text.color"] = text_color
    mpl.rcParams["axes.labelcolor"] = text_color
    mpl.rcParams["xtick.color"] = text_color
    mpl.rcParams["ytick.color"] = text_color

    # Figure background
    fig.patch.set_facecolor(bg_color)

    # Figure-level text elements (suptitle, supxlabel, supylabel)
    if hasattr(fig, "_suptitle") and fig._suptitle is not None:
        fig._suptitle.set_color(text_color)
    if hasattr(fig, "_supxlabel") and fig._supxlabel is not None:
        fig._supxlabel.set_color(text_color)
    if hasattr(fig, "_supylabel") and fig._supylabel is not None:
        fig._supylabel.set_color(text_color)

    for ax in fig.get_axes():
        _apply_dark_mode_to_axes(ax, bg_color, text_color)


def _apply_dark_mode_to_axes(ax: Axes, bg_color: str, text_color: str) -> None:
    """Apply dark mode colors to a single axes."""
    # Axes background
    ax.set_facecolor(bg_color)

    # Text colors
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)

    # Tick labels and tick marks
    ax.tick_params(colors=text_color, which="both")

    # Explicitly set tick label colors (for specgram and other plots)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(text_color)

    # Spines
    for spine in ax.spines.values():
        spine.set_color(text_color)

    # All text objects on axes (panel labels, pie labels, annotations)
    for text in ax.texts:
        text.set_color(text_color)

    # Stat annotation bracket lines (Line2D with clip_on=False)
    for line in ax.get_lines():
        # Bracket lines have clip_on=False and are typically black
        if not line.get_clip_on():
            current_color = line.get_color()
            # Only update if it's a dark color (black or near-black)
            if current_color in ["black", "k", "#000000", (0, 0, 0), (0.0, 0.0, 0.0)]:
                line.set_color(text_color)

    # Legend
    legend = ax.get_legend()
    if legend is not None:
        frame = legend.get_frame()
        frame.set_facecolor(bg_color)
        frame.set_edgecolor(text_color)
        for text in legend.get_texts():
            text.set_color(text_color)


__all__ = [
    "apply_overrides",
    "apply_color_palette",
    "apply_dark_mode",
]

# EOF

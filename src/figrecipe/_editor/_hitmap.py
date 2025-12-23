#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hitmap generation for interactive element selection.

This module generates color-coded images where each figure element
(line, scatter, bar, text, etc.) is rendered with a unique RGB color.
This enables precise pixel-based element detection when users click
on the figure preview.

The color encoding uses 24-bit RGB:
- First 12 elements: hand-picked visually distinct colors
- Elements 13+: HSV-based generation for deterministic uniqueness
"""

import io
from typing import Any, Dict, Tuple

from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.patches import Rectangle
from PIL import Image

# Hand-picked distinct colors for first 12 elements (maximum visual distinction)
DISTINCT_COLORS = [
    (255, 0, 0),  # Red
    (0, 200, 0),  # Green
    (0, 100, 255),  # Blue
    (255, 200, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 128, 0),  # Orange
    (128, 0, 255),  # Purple
    (0, 255, 128),  # Spring green
    (255, 0, 128),  # Rose
    (128, 255, 0),  # Lime
    (0, 128, 255),  # Sky blue
]

# Reserved colors
BACKGROUND_COLOR = (26, 26, 26)  # Dark gray for background
AXES_COLOR = (64, 64, 64)  # Medium gray for non-selectable axes elements


def id_to_rgb(element_id: int) -> Tuple[int, int, int]:
    """
    Convert element ID to unique RGB color.

    Parameters
    ----------
    element_id : int
        Unique element identifier (1-based).

    Returns
    -------
    tuple of int
        RGB color tuple (0-255 range).

    Notes
    -----
    - ID 0 is reserved for background
    - IDs 1-12 use hand-picked distinct colors
    - IDs 13+ use HSV-based generation
    """
    if element_id <= 0:
        return BACKGROUND_COLOR

    if element_id <= len(DISTINCT_COLORS):
        return DISTINCT_COLORS[element_id - 1]

    # HSV-based generation for IDs > 12
    # Use golden ratio for hue distribution
    golden_ratio = 0.618033988749895
    hue = ((element_id - len(DISTINCT_COLORS)) * golden_ratio) % 1.0

    # High saturation and value for visibility
    saturation = 0.7 + (element_id % 3) * 0.1  # 0.7-0.9
    value = 0.75 + (element_id % 4) * 0.0625  # 0.75-0.9375

    # HSV to RGB conversion
    return _hsv_to_rgb(hue, saturation, value)


def rgb_to_id(rgb: Tuple[int, int, int]) -> int:
    """
    Convert RGB color back to element ID.

    Parameters
    ----------
    rgb : tuple of int
        RGB color tuple.

    Returns
    -------
    int
        Element ID (0 if background/unknown).
    """
    if rgb == BACKGROUND_COLOR or rgb == AXES_COLOR:
        return 0

    # Check distinct colors first
    for i, color in enumerate(DISTINCT_COLORS):
        if rgb == color:
            return i + 1

    # For HSV-generated colors, we'd need reverse lookup
    # In practice, we use the color_map dict instead
    return 0


def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB (0-255 range)."""
    if s == 0.0:
        r = g = b = int(v * 255)
        return (r, g, b)

    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


def _normalize_color(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB 0-255 to matplotlib 0-1 format."""
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def _mpl_color_to_hex(color) -> str:
    """
    Convert matplotlib color to hex string for CSS.

    Parameters
    ----------
    color : str, tuple, or array-like
        Matplotlib color (name, hex, RGB/RGBA tuple 0-1 or 0-255).

    Returns
    -------
    str
        Hex color string like '#ff0000'.
    """
    import matplotlib.colors as mcolors

    try:
        # Handle named colors and hex strings
        if isinstance(color, str):
            rgba = mcolors.to_rgba(color)
        # Handle RGBA/RGB arrays (0-1 range from matplotlib)
        elif hasattr(color, "__len__"):
            if len(color) >= 3:
                # Check if it's 0-1 or 0-255 range
                if all(0 <= c <= 1 for c in color[:3]):
                    rgba = (
                        tuple(color[:3]) + (1.0,) if len(color) == 3 else tuple(color)
                    )
                else:
                    # Assume 0-255 range
                    rgba = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
            else:
                return "#888888"  # fallback
        else:
            return "#888888"  # fallback

        # Convert to hex
        r, g, b = int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#888888"  # fallback gray


def _detect_plot_types(fig) -> Dict[int, Dict[str, Any]]:
    """
    Detect plot types used on each axes from RecordingFigure.

    Parameters
    ----------
    fig : Figure or RecordingFigure
        Figure to analyze.

    Returns
    -------
    dict
        Mapping from ax_index to plot info:
        {ax_idx: {'types': set(), 'call_ids': {'boxplot': ['boxplot_000'], ...}}}
    """
    plot_info = {}

    # Check if fig is a RecordingFigure with record
    record = None
    if hasattr(fig, "record"):
        record = fig.record
    elif hasattr(fig, "fig") and hasattr(fig.fig, "_recording_figure"):
        # Wrapped figure
        record = (
            fig.fig._recording_figure.record
            if hasattr(fig.fig._recording_figure, "record")
            else None
        )

    if record is None:
        return plot_info

    # Analyze recorded calls
    axes_list = (
        fig.get_axes()
        if hasattr(fig, "get_axes")
        else (fig.fig.get_axes() if hasattr(fig, "fig") else [])
    )

    # Calculate ncols from record
    max_col = 0
    for ax_key in record.axes.keys():
        parts = ax_key.split("_")
        if len(parts) >= 3:
            max_col = max(max_col, int(parts[2]))
    ncols = max_col + 1

    for ax_key, ax_record in record.axes.items():
        # Parse ax position to index
        parts = ax_key.split("_")
        if len(parts) >= 3:
            row, col = int(parts[1]), int(parts[2])
            # Calculate axes index (row-major order for grid layouts)
            ax_idx = row * ncols + col

            if ax_idx < len(axes_list):
                if ax_idx not in plot_info:
                    plot_info[ax_idx] = {"types": set(), "call_ids": {}}

                for call in ax_record.calls:
                    if call.function in ("boxplot", "violinplot"):
                        plot_info[ax_idx]["types"].add(call.function)
                        if call.function not in plot_info[ax_idx]["call_ids"]:
                            plot_info[ax_idx]["call_ids"][call.function] = []
                        plot_info[ax_idx]["call_ids"][call.function].append(call.id)

    return plot_info


def _is_boxplot_element(line, ax) -> bool:
    """Check if a Line2D is part of a boxplot based on its properties."""
    label = line.get_label()
    # Boxplot elements typically have labels like "_child0", "_nolegend_"
    # - _childN: median lines (5 points), boxes
    # - _nolegend_: whiskers, caps (2 points)
    if label.startswith("_child"):
        # This is a boxplot median line or box element
        return True
    if label == "_nolegend_":
        # Check for whisker/cap (2-point lines)
        xdata, ydata = line.get_xdata(), line.get_ydata()
        if len(xdata) == 2 and len(ydata) == 2:
            return True
    return False


def _is_violin_element(coll, ax) -> bool:
    """Check if a PolyCollection is part of a violinplot."""
    # Violin bodies are PolyCollection with fill
    if hasattr(coll, "get_facecolor"):
        fc = coll.get_facecolor()
        if len(fc) > 0 and fc[0][3] > 0:  # Has visible fill
            return True
    return False


def generate_hitmap(
    fig: Figure,
    dpi: int = 150,
    include_text: bool = True,
) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Generate hitmap with unique colors per element.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to generate hitmap for.
    dpi : int, optional
        Resolution for hitmap rendering (default: 150).
    include_text : bool, optional
        Whether to include text elements like labels (default: True).

    Returns
    -------
    hitmap : PIL.Image.Image
        RGB image where each element has unique color.
    color_map : dict
        Mapping from element key to metadata:
        {
            'element_key': {
                'id': int,
                'type': str,  # 'line', 'scatter', 'bar', 'boxplot', 'violin', etc.
                'label': str,
                'ax_index': int,
                'rgb': [r, g, b],
            }
        }
    """
    # Store original properties for restoration
    original_props = {}
    color_map = {}
    element_id = 1

    # Detect plot types from record
    plot_types = _detect_plot_types(fig)

    # Get all axes (handle RecordingFigure wrapper)
    if hasattr(fig, "fig"):
        mpl_fig = fig.fig
    else:
        mpl_fig = fig
    axes_list = mpl_fig.get_axes()

    # Collect all artists and assign colors
    for ax_idx, ax in enumerate(axes_list):
        # Get plot info for this axes
        ax_info = plot_types.get(ax_idx, {"types": set(), "call_ids": {}})
        ax_plot_types = ax_info.get("types", set())
        ax_call_ids = ax_info.get("call_ids", {})
        has_boxplot = "boxplot" in ax_plot_types
        has_violin = "violinplot" in ax_plot_types

        # Get call_id for labeling
        boxplot_call_id = (
            ax_call_ids.get("boxplot", ["boxplot"])[0] if has_boxplot else None
        )
        violin_call_id = (
            ax_call_ids.get("violinplot", ["violin"])[0] if has_violin else None
        )

        # Process lines (traces)
        for i, line in enumerate(ax.get_lines()):
            if not line.get_visible():
                continue

            key = f"ax{ax_idx}_line{i}"
            rgb = id_to_rgb(element_id)

            original_props[key] = {
                "color": line.get_color(),
                "markerfacecolor": line.get_markerfacecolor(),
                "markeredgecolor": line.get_markeredgecolor(),
            }

            line.set_color(_normalize_color(rgb))
            line.set_markerfacecolor(_normalize_color(rgb))
            line.set_markeredgecolor(_normalize_color(rgb))

            # Determine element type
            orig_label = line.get_label() or f"line_{i}"
            if has_boxplot and (
                _is_boxplot_element(line, ax)
                or orig_label.startswith("_")  # All _-prefixed on boxplot axes
            ):
                elem_type = "boxplot"
                # Use call_id as label for grouping
                label = boxplot_call_id or "boxplot"
            elif has_violin and orig_label.startswith("_"):
                elem_type = "violin"
                label = violin_call_id or "violin"
            else:
                elem_type = "line"
                label = orig_label

            color_map[key] = {
                "id": element_id,
                "type": elem_type,
                "label": label,
                "ax_index": ax_idx,
                "rgb": list(rgb),
                "original_color": _mpl_color_to_hex(original_props[key]["color"]),
            }
            element_id += 1

        # Process scatter plots (PathCollection)
        for i, coll in enumerate(ax.collections):
            if isinstance(coll, PathCollection):
                if not coll.get_visible():
                    continue

                key = f"ax{ax_idx}_scatter{i}"
                rgb = id_to_rgb(element_id)

                original_props[key] = {
                    "facecolors": coll.get_facecolors().copy(),
                    "edgecolors": coll.get_edgecolors().copy(),
                }

                coll.set_facecolors([_normalize_color(rgb)])
                coll.set_edgecolors([_normalize_color(rgb)])

                # Get original facecolor for hover effect
                orig_fc = original_props[key]["facecolors"]
                orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

                color_map[key] = {
                    "id": element_id,
                    "type": "scatter",
                    "label": coll.get_label() or f"scatter_{i}",
                    "ax_index": ax_idx,
                    "rgb": list(rgb),
                    "original_color": _mpl_color_to_hex(orig_color),
                }
                element_id += 1

            elif isinstance(coll, PolyCollection):
                # Fill areas
                if not coll.get_visible():
                    continue

                key = f"ax{ax_idx}_fill{i}"
                rgb = id_to_rgb(element_id)

                original_props[key] = {
                    "facecolors": coll.get_facecolors().copy(),
                    "edgecolors": coll.get_edgecolors().copy(),
                }

                coll.set_facecolors([_normalize_color(rgb)])
                coll.set_edgecolors([_normalize_color(rgb)])

                # Get original facecolor for hover effect
                orig_fc = original_props[key]["facecolors"]
                orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

                # Determine element type
                orig_label = coll.get_label() or f"fill_{i}"
                if has_violin and _is_violin_element(coll, ax):
                    elem_type = "violin"
                    label = violin_call_id or "violin"
                else:
                    elem_type = "fill"
                    label = orig_label

                color_map[key] = {
                    "id": element_id,
                    "type": elem_type,
                    "label": label,
                    "ax_index": ax_idx,
                    "rgb": list(rgb),
                    "original_color": _mpl_color_to_hex(orig_color),
                }
                element_id += 1

        # Process bars (Rectangle patches)
        for i, patch in enumerate(ax.patches):
            if isinstance(patch, Rectangle):
                if not patch.get_visible():
                    continue
                # Skip axes frame rectangles
                if patch.get_width() == 1.0 and patch.get_height() == 1.0:
                    continue

                key = f"ax{ax_idx}_bar{i}"
                rgb = id_to_rgb(element_id)

                original_props[key] = {
                    "facecolor": patch.get_facecolor(),
                    "edgecolor": patch.get_edgecolor(),
                }

                patch.set_facecolor(_normalize_color(rgb))
                patch.set_edgecolor(_normalize_color(rgb))

                color_map[key] = {
                    "id": element_id,
                    "type": "bar",
                    "label": patch.get_label() or f"bar_{i}",
                    "ax_index": ax_idx,
                    "rgb": list(rgb),
                    "original_color": _mpl_color_to_hex(
                        original_props[key]["facecolor"]
                    ),
                }
                element_id += 1

        # Process images
        for i, img in enumerate(ax.images):
            if isinstance(img, AxesImage):
                if not img.get_visible():
                    continue

                key = f"ax{ax_idx}_image{i}"
                # Images can't be recolored, just track their bbox
                color_map[key] = {
                    "id": element_id,
                    "type": "image",
                    "label": f"image_{i}",
                    "ax_index": ax_idx,
                    "rgb": list(id_to_rgb(element_id)),
                }
                element_id += 1

        # Process text elements
        if include_text:
            # Title
            title = ax.get_title()
            if title:
                key = f"ax{ax_idx}_title"
                rgb = id_to_rgb(element_id)
                title_obj = ax.title

                original_props[key] = {"color": title_obj.get_color()}
                title_obj.set_color(_normalize_color(rgb))

                color_map[key] = {
                    "id": element_id,
                    "type": "title",
                    "label": "title",
                    "ax_index": ax_idx,
                    "rgb": list(rgb),
                }
                element_id += 1

            # X label
            xlabel = ax.get_xlabel()
            if xlabel:
                key = f"ax{ax_idx}_xlabel"
                rgb = id_to_rgb(element_id)
                xlabel_obj = ax.xaxis.label

                original_props[key] = {"color": xlabel_obj.get_color()}
                xlabel_obj.set_color(_normalize_color(rgb))

                color_map[key] = {
                    "id": element_id,
                    "type": "xlabel",
                    "label": "xlabel",
                    "ax_index": ax_idx,
                    "rgb": list(rgb),
                }
                element_id += 1

            # Y label
            ylabel = ax.get_ylabel()
            if ylabel:
                key = f"ax{ax_idx}_ylabel"
                rgb = id_to_rgb(element_id)
                ylabel_obj = ax.yaxis.label

                original_props[key] = {"color": ylabel_obj.get_color()}
                ylabel_obj.set_color(_normalize_color(rgb))

                color_map[key] = {
                    "id": element_id,
                    "type": "ylabel",
                    "label": "ylabel",
                    "ax_index": ax_idx,
                    "rgb": list(rgb),
                }
                element_id += 1

        # Process legend
        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            key = f"ax{ax_idx}_legend"
            rgb = id_to_rgb(element_id)

            # Store original frame color
            frame = legend.get_frame()
            original_props[key] = {
                "facecolor": frame.get_facecolor(),
                "edgecolor": frame.get_edgecolor(),
            }

            frame.set_facecolor(_normalize_color(rgb))
            frame.set_edgecolor(_normalize_color(rgb))

            color_map[key] = {
                "id": element_id,
                "type": "legend",
                "label": "legend",
                "ax_index": ax_idx,
                "rgb": list(rgb),
            }
            element_id += 1

    # Set non-selectable elements to axes color
    for ax in axes_list:
        # Spines
        for spine in ax.spines.values():
            spine.set_color(_normalize_color(AXES_COLOR))

        # Tick marks
        ax.tick_params(colors=_normalize_color(AXES_COLOR))

    # Set figure background
    fig.patch.set_facecolor(_normalize_color(BACKGROUND_COLOR))
    for ax in axes_list:
        ax.set_facecolor(_normalize_color(BACKGROUND_COLOR))

    # Render to buffer (use bbox_inches='tight' to match preview rendering)
    buf = io.BytesIO()
    fig.savefig(
        buf, format="png", dpi=dpi, facecolor=fig.get_facecolor(), bbox_inches="tight"
    )
    buf.seek(0)

    # Load as PIL Image
    hitmap = Image.open(buf).convert("RGB")

    # Restore original properties
    for ax_idx, ax in enumerate(axes_list):
        # Restore lines
        for i, line in enumerate(ax.get_lines()):
            key = f"ax{ax_idx}_line{i}"
            if key in original_props:
                props = original_props[key]
                line.set_color(props["color"])
                line.set_markerfacecolor(props["markerfacecolor"])
                line.set_markeredgecolor(props["markeredgecolor"])

        # Restore collections
        for i, coll in enumerate(ax.collections):
            if isinstance(coll, PathCollection):
                key = f"ax{ax_idx}_scatter{i}"
            elif isinstance(coll, PolyCollection):
                key = f"ax{ax_idx}_fill{i}"
            else:
                continue

            if key in original_props:
                props = original_props[key]
                coll.set_facecolors(props["facecolors"])
                coll.set_edgecolors(props["edgecolors"])

        # Restore patches
        for i, patch in enumerate(ax.patches):
            key = f"ax{ax_idx}_bar{i}"
            if key in original_props:
                props = original_props[key]
                patch.set_facecolor(props["facecolor"])
                patch.set_edgecolor(props["edgecolor"])

        # Restore text
        if include_text:
            key = f"ax{ax_idx}_title"
            if key in original_props:
                ax.title.set_color(original_props[key]["color"])

            key = f"ax{ax_idx}_xlabel"
            if key in original_props:
                ax.xaxis.label.set_color(original_props[key]["color"])

            key = f"ax{ax_idx}_ylabel"
            if key in original_props:
                ax.yaxis.label.set_color(original_props[key]["color"])

        # Restore legend
        key = f"ax{ax_idx}_legend"
        if key in original_props:
            legend = ax.get_legend()
            if legend:
                frame = legend.get_frame()
                props = original_props[key]
                frame.set_facecolor(props["facecolor"])
                frame.set_edgecolor(props["edgecolor"])

        # Restore spines
        for spine in ax.spines.values():
            spine.set_color("black")  # Default

        # Restore tick colors
        ax.tick_params(colors="black")

    # Restore backgrounds
    fig.patch.set_facecolor("white")
    for ax in axes_list:
        ax.set_facecolor("white")

    return hitmap, color_map


def hitmap_to_base64(hitmap: Image.Image) -> str:
    """
    Convert hitmap image to base64 string.

    Parameters
    ----------
    hitmap : PIL.Image.Image
        Hitmap image.

    Returns
    -------
    str
        Base64-encoded PNG string.
    """
    import base64

    buf = io.BytesIO()
    hitmap.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


__all__ = [
    "generate_hitmap",
    "hitmap_to_base64",
    "id_to_rgb",
    "rgb_to_id",
]

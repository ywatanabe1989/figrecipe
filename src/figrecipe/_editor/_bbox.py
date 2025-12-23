#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bounding box extraction for figure elements.

This module extracts pixel coordinates for all figure elements,
enabling precise hit detection and visual selection overlays.

Coordinate Pipeline:
    Matplotlib display coords (points) → inches → image pixels
"""

from typing import Any, Dict, List, Optional

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox


def extract_bboxes(
    fig: Figure,
    img_width: int,
    img_height: int,
    include_points: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """
    Extract bounding boxes for all figure elements.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to extract bboxes from.
    img_width : int
        Width of the output image in pixels.
    img_height : int
        Height of the output image in pixels.
    include_points : bool, optional
        Whether to include point arrays for lines/scatter (default: True).
        Enables proximity-based hit detection.

    Returns
    -------
    dict
        Mapping from element key to bbox info:
        {
            'element_key': {
                'x': float,      # Left edge in pixels
                'y': float,      # Top edge in pixels
                'width': float,  # Width in pixels
                'height': float, # Height in pixels
                'type': str,     # Element type
                'ax_index': int, # Axes index
                'points': [[x, y], ...],  # Optional path points
            }
        }
    """
    bboxes = {}

    # Get renderer for bbox calculations
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # Get tight bbox for coordinate transformation
    tight_bbox = fig.get_tightbbox(renderer)
    if tight_bbox is None:
        tight_bbox = Bbox.from_bounds(0, 0, fig.get_figwidth(), fig.get_figheight())

    # bbox_inches='tight' adds pad_inches (default 0.1) around the tight bbox
    pad_inches = 0.1
    saved_width_inches = tight_bbox.width + 2 * pad_inches
    saved_height_inches = tight_bbox.height + 2 * pad_inches

    # Calculate scale factors from saved image size to pixel size
    scale_x = img_width / saved_width_inches if saved_width_inches > 0 else 1
    scale_y = img_height / saved_height_inches if saved_height_inches > 0 else 1

    # Process each axes
    axes_list = fig.get_axes()
    for ax_idx, ax in enumerate(axes_list):
        # Axes bounding box
        ax_bbox = _get_element_bbox(
            ax,
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if ax_bbox:
            bboxes[f"ax{ax_idx}_axes"] = {
                **ax_bbox,
                "type": "axes",
                "ax_index": ax_idx,
            }

        # Lines
        for i, line in enumerate(ax.get_lines()):
            if not line.get_visible():
                continue

            key = f"ax{ax_idx}_line{i}"
            bbox = _get_line_bbox(
                line,
                ax,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
                include_points=include_points,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    "type": "line",
                    "label": line.get_label() or f"line_{i}",
                    "ax_index": ax_idx,
                }

        # Scatter plots
        scatter_idx = 0
        for i, coll in enumerate(ax.collections):
            if isinstance(coll, PathCollection):
                if not coll.get_visible():
                    continue

                key = f"ax{ax_idx}_scatter{scatter_idx}"
                bbox = _get_collection_bbox(
                    coll,
                    ax,
                    fig,
                    renderer,
                    tight_bbox,
                    img_width,
                    img_height,
                    scale_x,
                    scale_y,
                    pad_inches,
                    saved_height_inches,
                    include_points=include_points,
                )
                if bbox:
                    bboxes[key] = {
                        **bbox,
                        "type": "scatter",
                        "label": coll.get_label() or f"scatter_{scatter_idx}",
                        "ax_index": ax_idx,
                    }
                scatter_idx += 1

            elif isinstance(coll, PolyCollection):
                if not coll.get_visible():
                    continue

                key = f"ax{ax_idx}_fill{i}"
                bbox = _get_collection_bbox(
                    coll,
                    ax,
                    fig,
                    renderer,
                    tight_bbox,
                    img_width,
                    img_height,
                    scale_x,
                    scale_y,
                    pad_inches,
                    saved_height_inches,
                    include_points=False,  # Fills use bbox only
                )
                if bbox:
                    bboxes[key] = {
                        **bbox,
                        "type": "fill",
                        "label": coll.get_label() or f"fill_{i}",
                        "ax_index": ax_idx,
                    }

        # Bars
        bar_idx = 0
        for i, patch in enumerate(ax.patches):
            if isinstance(patch, Rectangle):
                if not patch.get_visible():
                    continue
                # Skip frame rectangles
                if patch.get_width() == 1.0 and patch.get_height() == 1.0:
                    continue

                key = f"ax{ax_idx}_bar{bar_idx}"
                bbox = _get_patch_bbox(
                    patch,
                    ax,
                    fig,
                    renderer,
                    tight_bbox,
                    img_width,
                    img_height,
                    scale_x,
                    scale_y,
                    pad_inches,
                    saved_height_inches,
                )
                if bbox:
                    bboxes[key] = {
                        **bbox,
                        "type": "bar",
                        "label": patch.get_label() or f"bar_{bar_idx}",
                        "ax_index": ax_idx,
                    }
                bar_idx += 1

        # Title
        title = ax.get_title()
        if title:
            key = f"ax{ax_idx}_title"
            bbox = _get_text_bbox(
                ax.title,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    "type": "title",
                    "label": "title",
                    "ax_index": ax_idx,
                    "text": title,
                }

        # X label (just the label text)
        xlabel = ax.get_xlabel()
        if xlabel:
            key = f"ax{ax_idx}_xlabel"
            bbox = _get_text_bbox(
                ax.xaxis.label,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    "type": "xlabel",
                    "label": "xlabel",
                    "ax_index": ax_idx,
                    "text": xlabel,
                }

        # X tick labels (separate hit region)
        xtick_bbox = _get_tick_labels_bbox(
            ax.xaxis,
            "x",
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if xtick_bbox:
            bboxes[f"ax{ax_idx}_xticks"] = {
                **xtick_bbox,
                "type": "xticks",
                "label": "x tick labels",
                "ax_index": ax_idx,
            }

        # Y label (just the label text)
        ylabel = ax.get_ylabel()
        if ylabel:
            key = f"ax{ax_idx}_ylabel"
            bbox = _get_text_bbox(
                ax.yaxis.label,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    "type": "ylabel",
                    "label": "ylabel",
                    "ax_index": ax_idx,
                    "text": ylabel,
                }

        # Y tick labels (separate hit region)
        ytick_bbox = _get_tick_labels_bbox(
            ax.yaxis,
            "y",
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if ytick_bbox:
            bboxes[f"ax{ax_idx}_yticks"] = {
                **ytick_bbox,
                "type": "yticks",
                "label": "y tick labels",
                "ax_index": ax_idx,
            }

        # Legend
        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            key = f"ax{ax_idx}_legend"
            try:
                legend_bbox = legend.get_window_extent(renderer)
                if legend_bbox is not None:
                    bbox = _transform_bbox(
                        legend_bbox,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes[key] = {
                            **bbox,
                            "type": "legend",
                            "label": "legend",
                            "ax_index": ax_idx,
                        }
            except Exception:
                pass

        # Spines (with padding for easier clicking)
        spine_min_size = 8  # Minimum hit region size in pixels
        for spine_name, spine in ax.spines.items():
            if spine.get_visible():
                key = f"ax{ax_idx}_spine_{spine_name}"
                try:
                    spine_bbox = spine.get_window_extent(renderer)
                    if spine_bbox is not None:
                        bbox = _transform_bbox(
                            spine_bbox,
                            fig,
                            tight_bbox,
                            img_width,
                            img_height,
                            scale_x,
                            scale_y,
                            pad_inches,
                            saved_height_inches,
                        )
                        if bbox:
                            # Expand thin spines for easier clicking
                            if bbox["width"] < spine_min_size:
                                expand = (spine_min_size - bbox["width"]) / 2
                                bbox["x"] -= expand
                                bbox["width"] = spine_min_size
                            if bbox["height"] < spine_min_size:
                                expand = (spine_min_size - bbox["height"]) / 2
                                bbox["y"] -= expand
                                bbox["height"] = spine_min_size
                            bboxes[key] = {
                                **bbox,
                                "type": "spine",
                                "label": spine_name,
                                "ax_index": ax_idx,
                            }
                except Exception:
                    pass

    # Process figure-level text elements (suptitle, supxlabel, supylabel)
    # Suptitle
    if hasattr(fig, "_suptitle") and fig._suptitle is not None:
        suptitle_obj = fig._suptitle
        if suptitle_obj.get_text():
            try:
                suptitle_extent = suptitle_obj.get_window_extent(renderer)
                if suptitle_extent is not None:
                    bbox = _transform_bbox(
                        suptitle_extent,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes["fig_suptitle"] = {
                            **bbox,
                            "type": "suptitle",
                            "label": "suptitle",
                            "ax_index": -1,  # Figure-level
                            "text": suptitle_obj.get_text(),
                        }
            except Exception:
                pass

    # Supxlabel
    if hasattr(fig, "_supxlabel") and fig._supxlabel is not None:
        supxlabel_obj = fig._supxlabel
        if supxlabel_obj.get_text():
            try:
                supxlabel_extent = supxlabel_obj.get_window_extent(renderer)
                if supxlabel_extent is not None:
                    bbox = _transform_bbox(
                        supxlabel_extent,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes["fig_supxlabel"] = {
                            **bbox,
                            "type": "supxlabel",
                            "label": "supxlabel",
                            "ax_index": -1,  # Figure-level
                            "text": supxlabel_obj.get_text(),
                        }
            except Exception:
                pass

    # Supylabel
    if hasattr(fig, "_supylabel") and fig._supylabel is not None:
        supylabel_obj = fig._supylabel
        if supylabel_obj.get_text():
            try:
                supylabel_extent = supylabel_obj.get_window_extent(renderer)
                if supylabel_extent is not None:
                    bbox = _transform_bbox(
                        supylabel_extent,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes["fig_supylabel"] = {
                            **bbox,
                            "type": "supylabel",
                            "label": "supylabel",
                            "ax_index": -1,  # Figure-level
                            "text": supylabel_obj.get_text(),
                        }
            except Exception:
                pass

    # Add metadata
    bboxes["_meta"] = {
        "img_width": img_width,
        "img_height": img_height,
        "fig_width_inches": fig.get_figwidth(),
        "fig_height_inches": fig.get_figheight(),
        "dpi": fig.dpi,
    }

    return bboxes


def _get_element_bbox(
    element,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a general element."""
    try:
        window_extent = element.get_window_extent(renderer)
        if window_extent is None:
            return None
        return _transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
    except Exception:
        return None


def _get_line_bbox(
    line,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
    include_points: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get bbox and points for a line."""
    try:
        # Get window extent
        window_extent = line.get_window_extent(renderer)
        if window_extent is None:
            return None

        bbox = _transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if bbox is None:
            return None

        # Add path points for proximity detection
        if include_points:
            xdata = line.get_xdata()
            ydata = line.get_ydata()

            if len(xdata) > 0 and len(ydata) > 0:
                # Transform data coords to image pixels
                transform = ax.transData
                points = []

                # Downsample if too many points
                max_points = 100
                step = max(1, len(xdata) // max_points)

                for i in range(0, len(xdata), step):
                    try:
                        display_coords = transform.transform((xdata[i], ydata[i]))
                        img_coords = _display_to_image(
                            display_coords[0],
                            display_coords[1],
                            fig,
                            tight_bbox,
                            img_width,
                            img_height,
                            scale_x,
                            scale_y,
                            pad_inches,
                            saved_height_inches,
                        )
                        if img_coords:
                            points.append(img_coords)
                    except Exception:
                        continue

                if points:
                    bbox["points"] = points

        return bbox

    except Exception:
        return None


def _get_collection_bbox(
    coll,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
    include_points: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get bbox and points for a collection (scatter, fill)."""
    try:
        bbox = None

        # For scatter plots, get_window_extent() can fail or return empty
        # So we calculate bbox from data points as fallback
        if isinstance(coll, PathCollection):
            offsets = coll.get_offsets()
            if len(offsets) > 0:
                transform = ax.transData
                points = []

                # Limit to reasonable number of points
                max_points = 200
                step = max(1, len(offsets) // max_points)

                for i in range(0, len(offsets), step):
                    try:
                        offset = offsets[i]
                        display_coords = transform.transform(offset)
                        img_coords = _display_to_image(
                            display_coords[0],
                            display_coords[1],
                            fig,
                            tight_bbox,
                            img_width,
                            img_height,
                            scale_x,
                            scale_y,
                            pad_inches,
                            saved_height_inches,
                        )
                        if img_coords:
                            points.append(img_coords)
                    except Exception:
                        continue

                # Calculate bbox from points
                if points:
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    # Add padding around scatter points for easier clicking
                    padding = 10  # pixels
                    bbox = {
                        "x": float(min(xs) - padding),
                        "y": float(min(ys) - padding),
                        "width": float(max(xs) - min(xs) + 2 * padding),
                        "height": float(max(ys) - min(ys) + 2 * padding),
                        "points": points,
                    }
                    return bbox

        # Fallback: try standard window extent
        window_extent = coll.get_window_extent(renderer)
        if window_extent is None:
            return None

        bbox = _transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )

        return bbox

    except Exception:
        return None


def _get_patch_bbox(
    patch,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a patch (bar, rectangle)."""
    try:
        window_extent = patch.get_window_extent(renderer)
        if window_extent is None:
            return None
        return _transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
    except Exception:
        return None


def _get_text_bbox(
    text,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a text element."""
    try:
        window_extent = text.get_window_extent(renderer)
        if window_extent is None:
            return None
        return _transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
    except Exception:
        return None


def _get_tick_labels_bbox(
    axis,
    axis_type: str,  # 'x' or 'y'
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """
    Get bbox for tick labels, extended to span the full axis dimension.

    For x-axis: tick labels bbox spans the full width of the plot area.
    For y-axis: tick labels bbox spans the full height of the plot area.
    """
    try:
        all_bboxes = []

        # Get all tick label bboxes
        for tick in axis.get_major_ticks():
            tick_label = tick.label1 if hasattr(tick, "label1") else tick.label
            if tick_label and tick_label.get_visible():
                try:
                    tick_extent = tick_label.get_window_extent(renderer)
                    if tick_extent is not None and tick_extent.width > 0:
                        all_bboxes.append(tick_extent)
                except Exception:
                    pass

        if not all_bboxes:
            return None

        # Merge all tick label bboxes
        merged = all_bboxes[0]
        for bbox in all_bboxes[1:]:
            merged = Bbox.union([merged, bbox])

        # Get the axes extent to extend the tick labels region
        ax = axis.axes
        ax_bbox = ax.get_window_extent(renderer)

        if axis_type == "x":
            # For x-axis: extend width to match axes width, keep tick labels height
            merged = Bbox.from_extents(
                ax_bbox.x0,  # Align left with axes
                merged.y0,  # Keep tick labels y position
                ax_bbox.x1,  # Align right with axes
                merged.y1,  # Keep tick labels height
            )
        else:  # y-axis
            # For y-axis: extend height to match axes height, keep tick labels width
            merged = Bbox.from_extents(
                merged.x0,  # Keep tick labels x position
                ax_bbox.y0,  # Align bottom with axes
                merged.x1,  # Keep tick labels width
                ax_bbox.y1,  # Align top with axes
            )

        return _transform_bbox(
            merged,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )

    except Exception:
        return None


def _transform_bbox(
    window_extent: Bbox,
    fig: Figure,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """
    Transform matplotlib window extent to image pixel coordinates.

    Parameters
    ----------
    window_extent : Bbox
        Bbox in display coordinates (points).
    fig : Figure
        Matplotlib figure.
    tight_bbox : Bbox
        Tight bbox of figure in inches.
    img_width, img_height : int
        Output image dimensions.
    scale_x, scale_y : float
        Scale factors from inches to pixels.
    pad_inches : float
        Padding added by bbox_inches='tight' (default 0.1).
    saved_height_inches : float
        Total saved image height including padding.

    Returns
    -------
    dict or None
        {x, y, width, height} in image pixels.
    """
    try:
        dpi = fig.dpi

        # Convert display coords to inches
        x0_inches = window_extent.x0 / dpi
        y0_inches = window_extent.y0 / dpi
        x1_inches = window_extent.x1 / dpi
        y1_inches = window_extent.y1 / dpi

        # Transform to saved image coordinates
        # Account for tight bbox origin and padding
        x0_rel = x0_inches - tight_bbox.x0 + pad_inches
        x1_rel = x1_inches - tight_bbox.x0 + pad_inches

        # Y coordinate flip: matplotlib Y=0 at bottom, image Y=0 at top
        y0_rel = saved_height_inches - (y1_inches - tight_bbox.y0 + pad_inches)
        y1_rel = saved_height_inches - (y0_inches - tight_bbox.y0 + pad_inches)

        # Scale to image pixels
        x0_px = x0_rel * scale_x
        y0_px = y0_rel * scale_y
        x1_px = x1_rel * scale_x
        y1_px = y1_rel * scale_y

        # Clamp to bounds
        x0_px = max(0, min(x0_px, img_width))
        x1_px = max(0, min(x1_px, img_width))
        y0_px = max(0, min(y0_px, img_height))
        y1_px = max(0, min(y1_px, img_height))

        width = x1_px - x0_px
        height = y1_px - y0_px

        if width <= 0 or height <= 0:
            return None

        return {
            "x": float(x0_px),
            "y": float(y0_px),
            "width": float(width),
            "height": float(height),
        }

    except Exception:
        return None


def _display_to_image(
    display_x: float,
    display_y: float,
    fig: Figure,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[List[float]]:
    """
    Transform display coordinates to image pixel coordinates.

    Returns
    -------
    list or None
        [x, y] in image pixels.
    """
    try:
        dpi = fig.dpi

        # Convert to inches
        x_inches = display_x / dpi
        y_inches = display_y / dpi

        # Transform to saved image coordinates with padding
        x_rel = x_inches - tight_bbox.x0 + pad_inches

        # Y coordinate flip: matplotlib Y=0 at bottom, image Y=0 at top
        y_rel = saved_height_inches - (y_inches - tight_bbox.y0 + pad_inches)

        # Scale to image pixels
        x_px = x_rel * scale_x
        y_px = y_rel * scale_y

        # Clamp
        x_px = max(0, min(x_px, img_width))
        y_px = max(0, min(y_px, img_height))

        return [float(x_px), float(y_px)]

    except Exception:
        return None


__all__ = ["extract_bboxes"]

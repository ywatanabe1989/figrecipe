#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure composition utilities for combining multiple figures.

This module provides a unified mm-based composition pipeline:
1. Grid-based layout: Automatic arrangement using layout solvers ('horizontal', 'vertical', 'grid')
2. Free-form positioning: Direct mm-based placement with canvas_size_mm and per-source xy_mm/size_mm

All layouts are solved to mm coordinates, then rendered through the same freeform pipeline.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from ._freeform import compose_freeform
from ._solvers import solve_layout
from ._utils import (
    add_caption,
    add_panel_labels,
    create_source_symlinks,
)


def _save_compose_recipe(
    output_path: Path,
    sources_mm: Dict[str, Dict[str, Any]],
    canvas_size_mm: Tuple[float, float],
    dpi: int,
    panel_labels: bool,
    label_style: str,
    caption: Optional[str],
    facecolor: str,
) -> Path:
    """Save composition layout as YAML recipe for future editing.

    The recipe stores all mm-based positioning, allowing users to:
    - Re-compose with adjusted positions
    - Change individual panel sizes without re-solving layout
    - Add/remove panels while keeping others in place
    """
    recipe = {
        "version": "1.0",
        "type": "compose",
        "canvas": {
            "size_mm": list(canvas_size_mm) if canvas_size_mm else None,
            "dpi": dpi,
            "facecolor": facecolor,
        },
        "panels": {
            path: {
                "xy_mm": list(spec["xy_mm"]),
                "size_mm": list(spec["size_mm"]),
            }
            for path, spec in sources_mm.items()
        },
        "style": {
            "panel_labels": panel_labels,
            "label_style": label_style,
            "caption": caption,
        },
    }

    recipe_path = output_path.with_suffix(".compose.yaml")
    with open(recipe_path, "w") as f:
        yaml.dump(recipe, f, default_flow_style=False, sort_keys=False)

    return recipe_path


def compose_figures(
    sources: Union[List[str], Dict[str, Dict[str, Any]]],
    output_path: str,
    layout: str = "horizontal",
    gap_mm: float = 5.0,
    dpi: int = 300,
    panel_labels: bool = True,
    label_style: str = "uppercase",
    label_fontsize: int = 10,
    label_fontweight: str = "bold",
    caption: Optional[str] = None,
    caption_fontsize: int = 8,
    create_symlinks: bool = True,
    canvas_size_mm: Optional[Tuple[float, float]] = None,
    facecolor: str = "white",
    save_recipe: bool = True,
) -> Dict[str, Any]:
    """Compose multiple figures into a single figure.

    Supports two modes:
    1. Grid-based layout (list sources): automatic arrangement with layout parameter
    2. Free-form positioning (dict sources): precise mm-based positioning

    Parameters
    ----------
    sources : list of str or dict
        Either:
        - List of paths to source images or recipe files (grid-based layout)
        - Dict mapping source paths to positioning specs with 'xy_mm' and 'size_mm':
          {"panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)}, ...}
    output_path : str
        Path to save the composed figure.
    layout : str
        Layout mode for list sources: 'horizontal', 'vertical', or 'grid'.
        Ignored when using dict sources with mm positioning.
    gap_mm : float
        Gap between panels in millimeters (for grid-based layout only).
    dpi : int
        DPI for output.
    panel_labels : bool
        If True, add panel labels (A, B, C, D) to each panel.
    label_style : str
        Label style: 'uppercase' (A, B, C), 'lowercase' (a, b, c), 'numeric' (1, 2, 3).
    label_fontsize : int
        Font size for panel labels.
    label_fontweight : str
        Font weight for panel labels ('bold', 'normal').
    caption : str, optional
        Figure caption to add below the composed figure.
    caption_fontsize : int
        Font size for caption.
    create_symlinks : bool
        If True (default), create symlinks to source files in a subdirectory
        for traceability and single source of truth.
    canvas_size_mm : tuple of (float, float), optional
        Canvas size as (width_mm, height_mm) for free-form positioning.
        Required when sources is a dict with mm positioning.
    facecolor : str
        Background color for the composed figure and all panels.
        Default is 'white'. Use this to ensure consistent backgrounds
        when source panels have different/transparent backgrounds.
    save_recipe : bool
        If True (default), save a YAML recipe file alongside the output.
        The recipe contains the solved mm positions for all panels,
        enabling future editing and re-composition.

    Returns
    -------
    dict
        Result with 'output_path', 'success', 'layout_spec', and optionally
        'sources_dir' (if symlinks) and 'recipe_path' (if save_recipe).

    Examples
    --------
    Grid-based layout (existing API):

    >>> compose_figures(
    ...     sources=["panel_a.png", "panel_b.png"],
    ...     output_path="figure.png",
    ...     layout="horizontal",
    ...     gap_mm=5.0,
    ... )

    Free-form mm-based positioning:

    >>> compose_figures(
    ...     canvas_size_mm=(180, 120),
    ...     sources={
    ...         "panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)},
    ...         "panel_b.yaml": {"xy_mm": (90, 0), "size_mm": (80, 50)},
    ...         "panel_c.yaml": {"xy_mm": (0, 60), "size_mm": (170, 50)},
    ...     },
    ...     output_path="figure.png",
    ... )
    """
    output_path = Path(output_path)

    # Unified pipeline: all layouts go through mm-based composition
    if isinstance(sources, dict):
        # Already mm-based positioning
        sources_mm = sources
        # canvas_size_mm is required for dict sources, but can be None for auto-calc
    else:
        # Solve layout to get mm positions
        sources_mm, canvas_size_mm = solve_layout(
            sources, layout, gap_mm, dpi, facecolor
        )

    # Single rendering path: mm-based composition
    result, positions, source_paths = compose_freeform(
        sources_mm, canvas_size_mm, dpi, facecolor
    )

    # Add panel labels if requested
    if panel_labels:
        result = add_panel_labels(
            result, positions, label_style, label_fontsize, label_fontweight, dpi
        )

    # Add caption if provided
    if caption:
        result = add_caption(result, caption, caption_fontsize, dpi)

    # Save result
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        result = result.convert("RGB")
    result.save(output_path, dpi=(dpi, dpi))

    result_dict = {
        "output_path": str(output_path),
        "success": True,
        # Include solved layout for recipe/traceability
        "layout_spec": {
            "canvas_size_mm": list(canvas_size_mm) if canvas_size_mm else None,
            "panels": {
                path: {
                    "xy_mm": list(spec["xy_mm"]),
                    "size_mm": list(spec["size_mm"]),
                }
                for path, spec in sources_mm.items()
            },
        },
    }

    # Create symlinks to source files for traceability
    if create_symlinks:
        sources_dir = create_source_symlinks(source_paths, output_path)
        if sources_dir:
            result_dict["sources_dir"] = str(sources_dir)

    # Save layout recipe for future editing
    if save_recipe:
        recipe_path = _save_compose_recipe(
            output_path,
            sources_mm,
            canvas_size_mm,
            dpi,
            panel_labels,
            label_style,
            caption,
            facecolor,
        )
        result_dict["recipe_path"] = str(recipe_path)

    return result_dict


def load_compose_recipe(recipe_path: str) -> Dict[str, Any]:
    """Load a composition recipe from YAML file.

    Parameters
    ----------
    recipe_path : str
        Path to the .compose.yaml recipe file.

    Returns
    -------
    dict
        Recipe containing canvas, panels, and style configuration.
    """
    with open(recipe_path) as f:
        return yaml.safe_load(f)


def recompose(
    recipe_path: str,
    output_path: Optional[str] = None,
    **overrides,
) -> Dict[str, Any]:
    """Re-compose a figure from a saved recipe with optional overrides.

    This allows editing the layout by:
    - Adjusting individual panel positions (via overrides)
    - Changing canvas size
    - Modifying style options

    Parameters
    ----------
    recipe_path : str
        Path to the .compose.yaml recipe file.
    output_path : str, optional
        Output path. If None, uses original path with '_recomposed' suffix.
    **overrides
        Override any recipe values. Examples:
        - canvas_size_mm=(200, 150)
        - panel_labels=False
        - panels={"path": {"xy_mm": [10, 10], ...}}

    Returns
    -------
    dict
        Result from compose_figures.
    """
    recipe = load_compose_recipe(recipe_path)

    # Build sources dict from recipe panels
    sources = {}
    panels = overrides.pop("panels", recipe.get("panels", {}))
    for path, spec in panels.items():
        sources[path] = {
            "xy_mm": tuple(spec["xy_mm"]),
            "size_mm": tuple(spec["size_mm"]),
        }

    # Determine output path
    if output_path is None:
        orig_path = Path(recipe_path).with_suffix("")
        if orig_path.suffix == ".compose":
            orig_path = orig_path.with_suffix("")
        output_path = str(orig_path) + "_recomposed.png"

    # Get canvas settings
    canvas = recipe.get("canvas", {})
    canvas_size_mm = overrides.pop("canvas_size_mm", canvas.get("size_mm"))
    if canvas_size_mm:
        canvas_size_mm = tuple(canvas_size_mm)
    dpi = overrides.pop("dpi", canvas.get("dpi", 300))
    facecolor = overrides.pop("facecolor", canvas.get("facecolor", "white"))

    # Get style settings
    style = recipe.get("style", {})
    panel_labels = overrides.pop("panel_labels", style.get("panel_labels", True))
    label_style = overrides.pop("label_style", style.get("label_style", "uppercase"))
    caption = overrides.pop("caption", style.get("caption"))

    return compose_figures(
        sources=sources,
        output_path=output_path,
        canvas_size_mm=canvas_size_mm,
        dpi=dpi,
        facecolor=facecolor,
        panel_labels=panel_labels,
        label_style=label_style,
        caption=caption,
        **overrides,
    )


__all__ = ["compose_figures", "load_compose_recipe", "recompose"]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mm-based figure composition with matplotlib.

Maintains full editability - no PIL image pasting.
All layouts are converted to matplotlib figure coordinates.
"""

import math
import string
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

# Type alias for return type
from matplotlib.figure import Figure

from .._serializer import load_recipe
from ._compose import _is_image_file


def compose_mm(
    sources: Dict[str, Dict[str, Any]],
    canvas_size_mm: Optional[Tuple[float, float]] = None,
    dpi: int = 300,
    panel_labels: bool = True,
    label_style: str = "uppercase",
    facecolor: str = "white",
    save_recipe: bool = True,
    **kwargs,
) -> Tuple[Figure, Dict[str, Any]]:
    """Compose figures with mm-based positioning.

    Parameters
    ----------
    sources : dict
        Mapping of source paths to positioning specs:
        {"panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)}, ...}
    canvas_size_mm : tuple, optional
        Canvas size as (width_mm, height_mm). If None, auto-calculated.
    dpi : int
        Output DPI.
    panel_labels : bool
        If True, add panel labels (A, B, C...).
    label_style : str
        Label style: 'uppercase', 'lowercase', 'numeric'.
    facecolor : str
        Background color.
    save_recipe : bool
        If True, composition metadata stored on figure.
    **kwargs
        Additional arguments.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Composed figure.
    axes_dict : dict
        Mapping of source paths to axes.
    """
    import matplotlib.pyplot as plt

    if not sources:
        raise ValueError("No sources provided for composition")

    # Validate source specs
    for path, spec in sources.items():
        if not isinstance(spec, dict):
            raise ValueError(
                f"Source spec for '{path}' must be a dict, got {type(spec).__name__}"
            )
        if "xy_mm" not in spec:
            raise ValueError(f"Source spec for '{path}' missing required key 'xy_mm'")
        if "size_mm" not in spec:
            raise ValueError(f"Source spec for '{path}' missing required key 'size_mm'")

    # Auto-calculate canvas size
    if canvas_size_mm is None:
        max_x = max(spec["xy_mm"][0] + spec["size_mm"][0] for spec in sources.values())
        max_y = max(spec["xy_mm"][1] + spec["size_mm"][1] for spec in sources.values())
        canvas_size_mm = (max_x, max_y)

    canvas_w_mm, canvas_h_mm = canvas_size_mm

    # Convert mm to inches
    canvas_w_in = canvas_w_mm / 25.4
    canvas_h_in = canvas_h_mm / 25.4

    # Create figure (regular matplotlib figure, not RecordingFigure)
    fig = plt.figure(figsize=(canvas_w_in, canvas_h_in), dpi=dpi, facecolor=facecolor)

    axes_dict = {}

    # Generate labels
    if label_style == "lowercase":
        labels = list(string.ascii_lowercase)
    elif label_style == "numeric":
        labels = [str(i + 1) for i in range(len(sources))]
    else:
        labels = list(string.ascii_uppercase)

    for idx, (source_path, spec) in enumerate(sources.items()):
        x_mm, y_mm = spec["xy_mm"]
        w_mm, h_mm = spec["size_mm"]

        # Convert mm to figure-relative coordinates [0, 1]
        left = x_mm / canvas_w_mm
        # Matplotlib y=0 is bottom, mm y=0 is top
        bottom = 1.0 - (y_mm + h_mm) / canvas_h_mm
        width = w_mm / canvas_w_mm
        height = h_mm / canvas_h_mm

        # Add axes at calculated position
        ax = fig.add_axes([left, bottom, width, height])

        # Load and replay source recipe
        path = Path(source_path)
        if path.suffix.lower() == ".yaml":
            source_record = load_recipe(path)
            ax_record = source_record.axes.get("ax_0_0")
            if ax_record:
                _replay_axes_record(ax, ax_record)
        elif _is_image_file(path):
            from PIL import Image

            img = Image.open(path)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            ax.imshow(np.array(img))
            ax.axis("off")

        # Add panel label
        if panel_labels and idx < len(labels):
            ax.text(
                0.02,
                0.98,
                labels[idx],
                transform=ax.transAxes,
                fontsize=10,
                fontweight="bold",
                va="top",
                ha="left",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
            )

        axes_dict[source_path] = ax

    # Store composition metadata on figure for reference
    if save_recipe:
        fig._compose_meta = {
            "canvas_size_mm": list(canvas_size_mm),
            "sources": {
                p: {"xy_mm": list(s["xy_mm"]), "size_mm": list(s["size_mm"])}
                for p, s in sources.items()
            },
            "panel_labels": panel_labels,
            "label_style": label_style,
            "facecolor": facecolor,
        }

    return fig, axes_dict


def _replay_axes_record(ax, ax_record) -> None:
    """Replay axes record onto matplotlib axes."""
    from .._reproducer._core import _replay_call

    result_cache: Dict[str, Any] = {}

    for call in ax_record.calls:
        result = _replay_call(ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    for call in ax_record.decorations:
        result = _replay_call(ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result


def solve_layout_to_mm(
    sources: list,
    layout: str = "horizontal",
    gap_mm: float = 5.0,
    panel_size_mm: Tuple[float, float] = (60, 45),
) -> Tuple[Dict[str, Dict[str, Any]], Tuple[float, float]]:
    """Solve layout to mm-based positioning.

    Parameters
    ----------
    sources : list
        List of source paths.
    layout : str
        Layout mode: 'horizontal', 'vertical', 'grid'.
    gap_mm : float
        Gap between panels in mm.
    panel_size_mm : tuple
        Default panel size (width_mm, height_mm).

    Returns
    -------
    sources_mm : dict
        Dict mapping paths to {"xy_mm": ..., "size_mm": ...}.
    canvas_size_mm : tuple
        Calculated canvas size.
    """
    w_mm, h_mm = panel_size_mm
    sources_mm = {}

    if layout == "horizontal":
        x = 0.0
        for path in sources:
            sources_mm[str(path)] = {"xy_mm": (x, 0.0), "size_mm": (w_mm, h_mm)}
            x += w_mm + gap_mm
        canvas_size_mm = (x - gap_mm if sources else 0.0, h_mm)

    elif layout == "vertical":
        y = 0.0
        for path in sources:
            sources_mm[str(path)] = {"xy_mm": (0.0, y), "size_mm": (w_mm, h_mm)}
            y += h_mm + gap_mm
        canvas_size_mm = (w_mm, y - gap_mm if sources else 0.0)

    elif layout == "grid":
        n = len(sources)
        ncols = math.ceil(math.sqrt(n)) if n > 0 else 1
        nrows = math.ceil(n / ncols) if n > 0 else 1

        for idx, path in enumerate(sources):
            row = idx // ncols
            col = idx % ncols
            x = col * (w_mm + gap_mm)
            y = row * (h_mm + gap_mm)
            sources_mm[str(path)] = {"xy_mm": (x, y), "size_mm": (w_mm, h_mm)}

        canvas_size_mm = (
            ncols * w_mm + (ncols - 1) * gap_mm,
            nrows * h_mm + (nrows - 1) * gap_mm,
        )

    else:
        raise ValueError(
            f"Unknown layout: {layout}. Use 'horizontal', 'vertical', 'grid'"
        )

    return sources_mm, canvas_size_mm


def compose_figures(
    sources,
    output_path: str,
    layout: str = "horizontal",
    gap_mm: float = 5.0,
    dpi: int = 300,
    panel_labels: bool = True,
    label_style: str = "uppercase",
    caption: Optional[str] = None,
    create_symlinks: bool = True,
    canvas_size_mm: Optional[Tuple[float, float]] = None,
    facecolor: str = "white",
    save_recipe: bool = True,
    **kwargs,
) -> Dict[str, Any]:
    """Compose multiple figures into a single figure (backward-compatible API).

    This is a wrapper around compose_mm that provides the same API as the
    previous PIL-based compose_figures, while using matplotlib internally
    for full reproducibility and editability.

    Parameters
    ----------
    sources : list of str or dict
        Either:
        - List of paths to source images or recipe files (grid-based layout)
        - Dict mapping source paths to positioning specs with 'xy_mm' and 'size_mm'
    output_path : str
        Path to save the composed figure.
    layout : str
        Layout mode for list sources: 'horizontal', 'vertical', or 'grid'.
    gap_mm : float
        Gap between panels in millimeters.
    dpi : int
        DPI for output.
    panel_labels : bool
        If True, add panel labels (A, B, C, D).
    label_style : str
        Style: 'uppercase' (A,B,C), 'lowercase' (a,b,c), 'numeric' (1,2,3).
    caption : str, optional
        Figure caption (added as text below figure).
    create_symlinks : bool
        If True (default), create symlinks to source files.
    canvas_size_mm : tuple of (float, float), optional
        Canvas size for free-form positioning.
    facecolor : str
        Background color (default: 'white').
    save_recipe : bool
        If True (default), save a .compose.yaml recipe file.

    Returns
    -------
    dict
        Result with 'output_path', 'success', 'layout_spec', and optionally
        'sources_dir' and 'recipe_path'.
    """
    import matplotlib.pyplot as plt
    import yaml

    output_path = Path(output_path)

    # Convert list sources to mm-based dict
    if isinstance(sources, list):
        sources_mm, auto_canvas = solve_layout_to_mm(
            sources, layout=layout, gap_mm=gap_mm
        )
        if canvas_size_mm is None:
            canvas_size_mm = auto_canvas
    else:
        sources_mm = sources
        if canvas_size_mm is not None:
            canvas_size_mm = tuple(canvas_size_mm)

    # Create composed figure using matplotlib-based compose_mm
    fig, axes_dict = compose_mm(
        sources=sources_mm,
        canvas_size_mm=canvas_size_mm,
        dpi=dpi,
        panel_labels=panel_labels,
        label_style=label_style,
        facecolor=facecolor,
        save_recipe=False,  # We handle recipe saving here
    )

    # Add caption if provided
    if caption:
        fig.text(0.5, 0.02, caption, ha="center", va="bottom", fontsize=8, wrap=True)

    # Save output
    fig.savefig(str(output_path), dpi=dpi, facecolor=fig.get_facecolor())

    result = {
        "output_path": str(output_path),
        "success": True,
        "layout_spec": {
            "canvas_size_mm": list(canvas_size_mm) if canvas_size_mm else None,
            "panels": {
                p: {"xy_mm": list(s["xy_mm"]), "size_mm": list(s["size_mm"])}
                for p, s in sources_mm.items()
            },
        },
    }

    # Create symlinks to source files
    if create_symlinks:
        sources_dir = output_path.parent / f"{output_path.stem}_sources"
        sources_dir.mkdir(exist_ok=True)
        for source_path in sources_mm.keys():
            src = Path(source_path)
            if src.exists():
                link = sources_dir / src.name
                if not link.exists():
                    try:
                        link.symlink_to(src.resolve())
                    except OSError:
                        pass  # Symlinks may not be supported
        result["sources_dir"] = str(sources_dir)

    # Save recipe YAML
    if save_recipe:
        recipe_path = output_path.with_suffix(".compose.yaml")
        recipe = {
            "version": "1.0",
            "type": "compose",
            "canvas": {
                "size_mm": list(canvas_size_mm) if canvas_size_mm else None,
                "dpi": dpi,
                "facecolor": facecolor,
            },
            "panels": result["layout_spec"]["panels"],
            "style": {
                "panel_labels": panel_labels,
                "label_style": label_style,
                "caption": caption,
            },
        }
        with open(recipe_path, "w") as f:
            yaml.dump(recipe, f, default_flow_style=False, sort_keys=False)
        result["recipe_path"] = str(recipe_path)

    plt.close(fig)

    return result


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
    import yaml

    with open(recipe_path) as f:
        return yaml.safe_load(f)


def recompose(
    recipe_path: str,
    output_path: Optional[str] = None,
    **overrides,
) -> Dict[str, Any]:
    """Re-compose a figure from a saved recipe with optional overrides.

    Parameters
    ----------
    recipe_path : str
        Path to the .compose.yaml recipe file.
    output_path : str, optional
        Output path. If None, uses original path with '_recomposed' suffix.
    **overrides
        Override any recipe values.

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


__all__ = [
    "compose_mm",
    "solve_layout_to_mm",
    "compose_figures",
    "load_compose_recipe",
    "recompose",
]

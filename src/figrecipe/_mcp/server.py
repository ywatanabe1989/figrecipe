#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP server for figrecipe - declarative matplotlib figure creation.

This module provides MCP tools for creating, reproducing, and managing
matplotlib figures through the figrecipe library.

Usage:
    fastmcp run figrecipe._mcp.server:mcp
    # or
    figrecipe mcp run
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastmcp import FastMCP

from .._branding import get_mcp_instructions, get_mcp_server_name
from ._diagram_tools import register_diagram_tools
from ._resources import register_resources

mcp = FastMCP(
    name=get_mcp_server_name(),
    instructions=get_mcp_instructions(),
)


@mcp.tool
def plot(
    spec: Dict[str, Any],
    output_path: str,
    dpi: int = 300,
    save_recipe: bool = True,
) -> Dict[str, Any]:
    """Create a matplotlib figure from a declarative specification.

    See figrecipe._api._plot module docstring for full spec format.

    Parameters
    ----------
    spec : dict
        Declarative specification. Key sections: figure, plots, stat_annotations,
        xlabel, ylabel, title, legend, xlim, ylim.
    output_path : str
        Path to save the output figure.
    dpi : int
        DPI for raster output (default: 300).
    save_recipe : bool
        If True, also save as figrecipe YAML recipe.

    Returns
    -------
    dict
        Result with 'image_path' and 'recipe_path'.

    Raises
    ------
    ValueError
        If no plots are specified or data is missing.
    """
    from .._api._plot import create_figure_from_spec

    # Validate spec has plots with data
    plots = spec.get("plots", [])
    axes_specs = spec.get("axes") or spec.get("subplots", [])
    if not plots and not axes_specs:
        raise ValueError("No plots specified in spec. Add 'plots' or 'axes' section.")
    for i, p in enumerate(plots):
        if not (p.get("x") or p.get("y") or p.get("data") or p.get("z")):
            raise ValueError(f"Plot {i} has no data (x, y, data, or z required)")

    result = create_figure_from_spec(
        spec=spec,
        output_path=output_path,
        dpi=dpi,
        save_recipe=save_recipe,
        show=False,
    )

    return {
        "image_path": str(result["image_path"]) if result["image_path"] else None,
        "recipe_path": str(result["recipe_path"])
        if result.get("recipe_path")
        else None,
        "success": True,
    }


@mcp.tool
def reproduce(
    recipe_path: str,
    output_path: Optional[str] = None,
    format: str = "png",
    dpi: int = 300,
) -> Dict[str, Any]:
    """Reproduce a figure from a saved YAML recipe.

    Parameters
    ----------
    recipe_path : str
        Path to the .yaml recipe file.

    output_path : str, optional
        Output path for the reproduced figure.
        Defaults to recipe_path with .reproduced.{format} suffix.

    format : str
        Output format: png, pdf, or svg.

    dpi : int
        DPI for raster output.

    Returns
    -------
    dict
        Result with 'output_path' and 'success'.
    """
    import matplotlib.pyplot as plt

    import figrecipe as fr

    recipe_path = Path(recipe_path)

    if output_path is None:
        output_path = recipe_path.with_suffix(f".reproduced.{format}")
    else:
        output_path = Path(output_path)

    fig, axes = fr.reproduce(recipe_path)
    fig.savefig(output_path, dpi=dpi, format=format)

    try:
        plt.close(fig)
    except TypeError:
        plt.close("all")

    return {
        "output_path": str(output_path),
        "success": True,
    }


@mcp.tool
def compose(
    sources: List[str],
    output_path: str,
    layout: str = "horizontal",
    gap_mm: float = 5.0,
    dpi: int = 300,
    panel_labels: bool = True,
    label_style: str = "uppercase",
    caption: Optional[str] = None,
    create_symlinks: bool = True,
    canvas_size_mm: Optional[Tuple[float, float]] = None,
) -> Dict[str, Any]:
    """Compose multiple figures into a single figure with panel labels.

    Supports two modes:
    1. Grid-based layout (list sources): automatic arrangement with layout parameter
    2. Free-form positioning (dict sources): precise mm-based positioning

    Parameters
    ----------
    sources : list of str or dict
        Either:
        - List of paths to source images or recipe files (grid-based layout)
        - Dict mapping source paths to positioning specs with 'xy_mm' and 'size_mm':
          {"panel_a.yaml": {"xy_mm": [0, 0], "size_mm": [80, 50]}, ...}
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
        If True, add panel labels (A, B, C, D) automatically.
    label_style : str
        Style: 'uppercase' (A,B,C), 'lowercase' (a,b,c), 'numeric' (1,2,3).
    caption : str, optional
        Figure caption to add below.
    create_symlinks : bool
        If True (default), create symlinks to source files for traceability.
    canvas_size_mm : tuple of (float, float), optional
        Canvas size as (width_mm, height_mm) for free-form positioning.
        Required when sources is a dict with mm positioning.

    Returns
    -------
    dict
        Result with 'output_path', 'success', and 'sources_dir' (if symlinks created).

    Examples
    --------
    Grid-based layout:

    >>> compose(
    ...     sources=["panel_a.png", "panel_b.png"],
    ...     output_path="figure.png",
    ...     layout="horizontal",
    ... )

    Free-form mm-based positioning:

    >>> compose(
    ...     canvas_size_mm=[180, 120],
    ...     sources={
    ...         "panel_a.yaml": {"xy_mm": [0, 0], "size_mm": [80, 50]},
    ...         "panel_b.yaml": {"xy_mm": [90, 0], "size_mm": [80, 50]},
    ...     },
    ...     output_path="figure.png",
    ... )
    """
    from .._api._compose import compose_figures

    return compose_figures(
        sources=sources,
        output_path=output_path,
        layout=layout,
        gap_mm=gap_mm,
        dpi=dpi,
        panel_labels=panel_labels,
        label_style=label_style,
        caption=caption,
        create_symlinks=create_symlinks,
        canvas_size_mm=canvas_size_mm,
    )


@mcp.tool
def info(recipe_path: str, verbose: bool = False) -> Dict[str, Any]:
    """Get information about a recipe file.

    Parameters
    ----------
    recipe_path : str
        Path to the .yaml recipe file.

    verbose : bool
        If True, include detailed call information.

    Returns
    -------
    dict
        Recipe information including figure dimensions, call counts, etc.
    """
    import figrecipe as fr

    recipe_info = fr.info(recipe_path)
    return recipe_info


@mcp.tool
def validate(
    recipe_path: str,
    mse_threshold: float = 100.0,
) -> Dict[str, Any]:
    """Validate that a recipe can reproduce its original figure.

    Parameters
    ----------
    recipe_path : str
        Path to the .yaml recipe file.

    mse_threshold : float
        Maximum acceptable mean squared error (default: 100).

    Returns
    -------
    dict
        Validation result with 'passed', 'mse', and details.
    """
    import figrecipe as fr

    result = fr.validate(recipe_path, mse_threshold=mse_threshold)

    return {
        "valid": result.valid,
        "mse": result.mse,
        "message": result.message,
        "recipe_path": str(recipe_path),
    }


@mcp.tool
def crop(
    input_path: str,
    output_path: Optional[str] = None,
    margin_mm: float = 1.0,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Crop whitespace from a figure image.

    Parameters
    ----------
    input_path : str
        Path to the input image.

    output_path : str, optional
        Path for cropped output. Defaults to input with .cropped suffix.

    margin_mm : float
        Margin to keep around content in millimeters.

    overwrite : bool
        If True, overwrite the input file.

    Returns
    -------
    dict
        Result with 'output_path' and 'success'.
    """
    import figrecipe as fr

    result_path = fr.crop(
        input_path,
        output_path=output_path,
        margin_mm=margin_mm,
        overwrite=overwrite,
    )

    return {
        "output_path": str(result_path),
        "success": True,
    }


@mcp.tool
def extract_data(recipe_path: str) -> Dict[str, Dict[str, Any]]:
    """Extract plotted data arrays from a saved recipe.

    Parameters
    ----------
    recipe_path : str
        Path to the .yaml recipe file.

    Returns
    -------
    dict
        Nested dict: {call_id: {'x': list, 'y': list, ...}}
    """
    import figrecipe as fr

    data = fr.extract_data(recipe_path)

    # Convert numpy arrays to lists for JSON serialization
    result = {}
    for call_id, call_data in data.items():
        result[call_id] = {}
        for key, value in call_data.items():
            if hasattr(value, "tolist"):
                result[call_id][key] = value.tolist()
            else:
                result[call_id][key] = value

    return result


@mcp.tool
def list_styles() -> Dict[str, Any]:
    """List available figure style presets.

    Returns
    -------
    dict
        Dictionary with 'presets' list of available style names.
    """
    import figrecipe as fr

    presets = fr.list_presets()

    return {
        "presets": presets,
        "count": len(presets),
    }


@mcp.tool
def get_plot_types() -> Dict[str, Any]:
    """Get list of supported plot types.

    Returns
    -------
    dict
        Dictionary with 'plot_types' and their descriptions.
    """
    from .._api._plot import PLOT_TYPES

    return {
        "plot_types": list(PLOT_TYPES.keys()),
        "mapping": PLOT_TYPES,
        "categories": {
            "line_curve": ["line", "plot", "step", "fill", "fill_between", "errorbar"],
            "scatter_points": ["scatter"],
            "bar_categorical": ["bar", "barh"],
            "distribution": [
                "hist",
                "hist2d",
                "boxplot",
                "box",
                "violinplot",
                "violin",
            ],
            "image_matrix": ["imshow", "matshow", "heatmap", "pcolormesh"],
            "contour": ["contour", "contourf"],
            "special": ["pie", "stem", "eventplot", "hexbin"],
        },
    }


# Resource for spec schema documentation
@mcp.resource("figrecipe://spec-schema")
def get_spec_schema() -> str:
    """Get the declarative plot specification schema from API module."""
    from .._api import _plot

    # Return the module docstring as single source of truth
    schema = _plot.__doc__ or ""

    # Append supported plot types
    from .._api._plot import PLOT_TYPES

    schema += "\n\nSupported Plot Types\n"
    schema += "--------------------\n"
    schema += ", ".join(sorted(PLOT_TYPES.keys()))

    return schema


# Register additional documentation resources
register_resources(mcp)

# Register diagram tools

register_diagram_tools(mcp)


if __name__ == "__main__":
    mcp.run()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figrecipe - Record and reproduce matplotlib figures.

A lightweight library for capturing matplotlib plotting calls and
reproducing figures from saved recipes.

Usage
-----
Option 1: Import as module (recommended for explicit usage)

>>> import figrecipe as ps
>>> fig, ax = ps.subplots()
>>> ax.plot(x, y, id='my_data')
>>> ps.save(fig, 'recipe.yaml')

Option 2: Drop-in replacement for matplotlib.pyplot

>>> import figrecipe.pyplot as plt  # Instead of: import matplotlib.pyplot as plt
>>> fig, ax = plt.subplots()  # Automatically recording-enabled
>>> ax.plot(x, y, id='my_data')
>>> fig.save_recipe('recipe.yaml')

Examples
--------
Recording a figure:

>>> import figrecipe as ps
>>> import numpy as np
>>>
>>> x = np.linspace(0, 10, 100)
>>> y = np.sin(x)
>>>
>>> fig, ax = ps.subplots()
>>> ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
>>> ax.set_xlabel('Time')
>>> ax.set_ylabel('Amplitude')
>>> ps.save(fig, 'my_figure.yaml')

Reproducing a figure:

>>> fig, ax = ps.reproduce('my_figure.yaml')
>>> plt.show()

Inspecting a recipe:

>>> info = ps.info('my_figure.yaml')
>>> print(info['calls'])
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray

# Notebook utilities
from ._api._notebook import enable_svg

# Panel label
from ._api._panel import panel_label

# Seaborn proxy
from ._api._seaborn_proxy import sns

# Composition API
from ._composition import (
    AlignmentMode,
    align_panels,
    compose,
    distribute_panels,
    hide_panel,
    import_axes,
    show_panel,
    smart_align,
    toggle_panel,
)

# scitex.stats integration
from ._integrations import (
    SCITEX_STATS_AVAILABLE,
    annotate_from_stats,
    from_scitex_stats,
)
from ._recorder import CallRecord, FigureRecord
from ._reproducer import get_recipe_info
from ._reproducer import reproduce as _reproduce
from ._serializer import load_recipe
from ._utils._numpy_io import DataFormat
from ._utils._units import (
    inch_to_mm,
    mm_to_inch,
    mm_to_pt,
    mm_to_scatter_size,
    normalize_color,
    pt_to_mm,
)
from ._validator import ValidationResult
from ._wrappers import RecordingAxes, RecordingFigure
from .styles._style_applier import check_font, list_available_fonts

__version__ = "0.7.6"
__all__ = [
    # Main API
    "subplots",
    "save",
    "reproduce",
    "info",
    "load",
    "extract_data",
    "validate",
    # GUI Editor
    "edit",
    # Style system
    "load_style",
    "unload_style",
    "list_presets",
    "STYLE",
    "apply_style",
    # Unit conversions
    "mm_to_inch",
    "mm_to_pt",
    "inch_to_mm",
    "pt_to_mm",
    "mm_to_scatter_size",
    "normalize_color",
    # Font utilities
    "list_available_fonts",
    "check_font",
    # Notebook utilities
    "enable_svg",
    # Seaborn support
    "sns",
    # Classes (for type hints)
    "RecordingFigure",
    "RecordingAxes",
    "FigureRecord",
    "CallRecord",
    "ValidationResult",
    # Image utilities
    "crop",
    # Panel labels
    "panel_label",
    # Composition
    "compose",
    "import_axes",
    "hide_panel",
    "show_panel",
    "toggle_panel",
    # Alignment
    "AlignmentMode",
    "align_panels",
    "distribute_panels",
    "smart_align",
    # scitex.stats integration
    "from_scitex_stats",
    "annotate_from_stats",
    "SCITEX_STATS_AVAILABLE",
    # Version
    "__version__",
]


# Style management
from ._api._style_manager import (
    STYLE,
    apply_style,
    list_presets,
    load_style,
    unload_style,
)


def subplots(
    nrows: int = 1,
    ncols: int = 1,
    # MM-control parameters
    axes_width_mm: Optional[float] = None,
    axes_height_mm: Optional[float] = None,
    margin_left_mm: Optional[float] = None,
    margin_right_mm: Optional[float] = None,
    margin_bottom_mm: Optional[float] = None,
    margin_top_mm: Optional[float] = None,
    space_w_mm: Optional[float] = None,
    space_h_mm: Optional[float] = None,
    # Style parameters
    style: Optional[Dict[str, Any]] = None,
    apply_style_mm: bool = True,
    # Panel labels (None = use style default, True/False = explicit)
    panel_labels: Optional[bool] = None,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray]]:
    """Create a figure with recording-enabled axes.

    This is a drop-in replacement for plt.subplots() that wraps the
    returned figure and axes with recording capabilities.

    Supports mm-based layout control for publication-quality figures.

    Parameters
    ----------
    nrows, ncols : int
        Number of rows and columns of subplots.
    axes_width_mm, axes_height_mm : float, optional
        Axes dimensions in mm.
    margin_left_mm, margin_right_mm : float, optional
        Left/right margins in mm.
    margin_bottom_mm, margin_top_mm : float, optional
        Bottom/top margins in mm.
    space_w_mm, space_h_mm : float, optional
        Horizontal/vertical spacing between axes in mm.
    style : dict, optional
        Style configuration dictionary.
    apply_style_mm : bool
        If True (default), apply loaded style to axes.
    panel_labels : bool or None
        If True, add panel labels (A, B, C, ...).
    **kwargs
        Additional arguments passed to plt.subplots().

    Returns
    -------
    fig : RecordingFigure
        Wrapped figure object.
    axes : RecordingAxes or ndarray
        Wrapped axes.
    """
    from ._api._subplots import create_subplots

    return create_subplots(
        nrows=nrows,
        ncols=ncols,
        axes_width_mm=axes_width_mm,
        axes_height_mm=axes_height_mm,
        margin_left_mm=margin_left_mm,
        margin_right_mm=margin_right_mm,
        margin_bottom_mm=margin_bottom_mm,
        margin_top_mm=margin_top_mm,
        space_w_mm=space_w_mm,
        space_h_mm=space_h_mm,
        style=style,
        apply_style_mm=apply_style_mm,
        panel_labels=panel_labels,
        **kwargs,
    )


def save(
    fig: Union[RecordingFigure, Figure],
    path: Union[str, Path],
    include_data: bool = True,
    data_format: DataFormat = "csv",
    validate: bool = True,
    validate_mse_threshold: float = 100.0,
    validate_error_level: str = "error",
    verbose: bool = True,
    dpi: Optional[int] = None,
    image_format: Optional[str] = None,
):
    """Save a figure as image and recipe.

    Automatically saves both the image file and the YAML recipe for
    reproducibility. Specify either image or YAML path - the other
    will be created with the same base name.

    Parameters
    ----------
    fig : RecordingFigure or Figure
        The figure to save.
    path : str or Path
        Output path (.png, .pdf, .svg, .yaml, etc.)
    include_data : bool
        If True, save large arrays to separate files.
    data_format : str
        Format for data files: 'csv', 'npz', or 'inline'.
    validate : bool
        If True (default), validate reproducibility after saving.
    validate_mse_threshold : float
        Maximum acceptable MSE for validation (default: 100).
    validate_error_level : str
        How to handle validation failures: 'error', 'warning', or 'debug'.
    verbose : bool
        If True (default), print save status.
    dpi : int, optional
        DPI for image output.
    image_format : str, optional
        Image format when path is YAML.

    Returns
    -------
    tuple
        (image_path, yaml_path, ValidationResult or None)
    """
    from ._api._save import save_figure

    return save_figure(
        fig=fig,
        path=path,
        include_data=include_data,
        data_format=data_format,
        validate=validate,
        validate_mse_threshold=validate_mse_threshold,
        validate_error_level=validate_error_level,
        verbose=verbose,
        dpi=dpi,
        image_format=image_format,
    )


def reproduce(
    path: Union[str, Path],
    calls: Optional[List[str]] = None,
    skip_decorations: bool = False,
) -> Tuple[Figure, Union[Axes, List[Axes]]]:
    """Reproduce a figure from a recipe file.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.
    calls : list of str, optional
        If provided, only reproduce these specific call IDs.
    skip_decorations : bool
        If True, skip decoration calls.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Reproduced figure.
    axes : Axes or list of Axes
        Reproduced axes.
    """
    return _reproduce(path, calls=calls, skip_decorations=skip_decorations)


def info(path: Union[str, Path]) -> Dict[str, Any]:
    """Get information about a recipe without reproducing."""
    return get_recipe_info(path)


def load(path: Union[str, Path]) -> FigureRecord:
    """Load a recipe as a FigureRecord object."""
    return load_recipe(path)


def extract_data(path: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
    """Extract data arrays from a saved recipe.

    Returns
    -------
    dict
        Nested dictionary: {call_id: {'x': array, 'y': array, ...}}
    """
    from ._api._extract import DECORATION_FUNCS, extract_call_data

    record = load_recipe(path)
    result = {}

    for ax_key, ax_record in record.axes.items():
        for call in ax_record.calls:
            if call.function in DECORATION_FUNCS:
                continue
            call_data = extract_call_data(call)
            if call_data:
                result[call.id] = call_data

    return result


def validate(
    path: Union[str, Path],
    mse_threshold: float = 100.0,
) -> ValidationResult:
    """Validate that a saved recipe can reproduce its original figure.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.
    mse_threshold : float
        Maximum acceptable MSE for validation to pass (default: 100).

    Returns
    -------
    ValidationResult
        Detailed comparison results.
    """
    from ._api._validate import validate_recipe

    return validate_recipe(path, mse_threshold)


def crop(
    input_path,
    output_path=None,
    margin_mm=1.0,
    margin_px=None,
    overwrite=False,
    verbose=False,
):
    """Crop a figure image to its content area with a specified margin.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image.
    output_path : str or Path, optional
        Path to save the cropped image.
    margin_mm : float, optional
        Margin in millimeters (default: 1.0mm).
    margin_px : int, optional
        Margin in pixels (overrides margin_mm if provided).
    overwrite : bool, optional
        Whether to overwrite the input file (default: False)
    verbose : bool, optional
        Whether to print detailed information (default: False)

    Returns
    -------
    Path
        Path to the saved cropped image.
    """
    from ._utils._crop import crop as _crop

    return _crop(input_path, output_path, margin_mm, margin_px, overwrite, verbose)


def edit(
    source=None,
    style=None,
    port: int = 5050,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    hot_reload: bool = False,
):
    """Launch interactive GUI editor for figure styling.

    Parameters
    ----------
    source : RecordingFigure, str, Path, or None
        Either a live RecordingFigure object, path to a .yaml recipe file,
        or None to create a new blank figure.
    style : str or dict, optional
        Style preset name or style dict.
    port : int, optional
        Flask server port (default: 5050).
    host : str, optional
        Host to bind Flask server (default: "127.0.0.1", use "0.0.0.0" for Docker).
    open_browser : bool, optional
        Whether to open browser automatically (default: True).
    hot_reload : bool, optional
        Enable hot reload (default: False).

    Returns
    -------
    dict
        Final style overrides after editing session.
    """
    from ._editor import edit as _edit

    return _edit(
        source,
        style=style,
        port=port,
        host=host,
        open_browser=open_browser,
        hot_reload=hot_reload,
    )

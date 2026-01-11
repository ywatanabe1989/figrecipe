#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figrecipe - Record and reproduce matplotlib figures.

A lightweight library for capturing matplotlib plotting calls and
reproducing figures from saved recipes.

Usage
-----
>>> import figrecipe as fr
>>> fig, ax = fr.subplots()
>>> ax.plot(x, y, id='my_data')
>>> fr.save(fig, 'recipe.yaml')

Examples
--------
Recording a figure:

>>> import figrecipe as fr
>>> import numpy as np
>>>
>>> x = np.linspace(0, 10, 100)
>>> y = np.sin(x)
>>>
>>> fig, ax = fr.subplots()
>>> ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
>>> ax.set_xlabel('Time')
>>> ax.set_ylabel('Amplitude')
>>> fr.save(fig, 'my_figure.yaml')

Reproducing a figure:

>>> fig, ax = fr.reproduce('my_figure.yaml')
>>> plt.show()

Utility Functions
-----------------
For advanced use cases, utility functions are available via the utils submodule:

>>> from figrecipe import utils
>>> utils.mm_to_inch(25.4)  # Unit conversions
>>> utils.check_font('Arial')  # Font utilities
>>> utils.load_recipe('recipe.yaml')  # Low-level recipe access
"""

# Internal imports (hidden from tab completion with underscore prefix)
from pathlib import Path as _Path
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

from matplotlib.axes import Axes as _Axes
from matplotlib.figure import Figure as _Figure
from numpy.typing import NDArray as _NDArray

# Internal module imports (underscore prefixed for hiding)
from ._api._notebook import enable_svg
from ._api._seaborn_proxy import sns
from ._composition import (
    align_panels,
    compose,
    distribute_panels,
    smart_align,
)

# Graph visualization
from ._graph_presets import (
    get_preset as get_graph_preset,
)
from ._graph_presets import (
    list_presets as list_graph_presets,
)
from ._graph_presets import (
    register_preset as register_graph_preset,
)
from ._recorder import FigureRecord as _FigureRecord
from ._reproducer import get_recipe_info as _get_recipe_info
from ._reproducer import reproduce as _reproduce
from ._serializer import load_recipe as _load_recipe
from ._utils._numpy_io import CsvFormat as _CsvFormat
from ._utils._numpy_io import DataFormat as _DataFormat
from ._validator import ValidationResult as _ValidationResult
from ._wrappers import RecordingAxes as _RecordingAxes
from ._wrappers import RecordingFigure as _RecordingFigure

try:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("figrecipe")
except Exception:
    __version__ = "0.0.0"  # Fallback for development
__all__ = [
    # Core (essential)
    "subplots",
    "save",
    "reproduce",
    "load",  # Alias for reproduce
    "info",
    "edit",
    "validate",
    "crop",
    "extract_data",
    # Style
    "load_style",
    "unload_style",
    "list_presets",
    "apply_style",
    "STYLE",
    # Composition (simplified)
    "compose",
    "align_panels",
    "distribute_panels",
    "smart_align",
    # Graph visualization
    "get_graph_preset",
    "list_graph_presets",
    "register_graph_preset",
    # Extensions
    "sns",
    "enable_svg",
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
    axes_width_mm: _Optional[float] = None,
    axes_height_mm: _Optional[float] = None,
    margin_left_mm: _Optional[float] = None,
    margin_right_mm: _Optional[float] = None,
    margin_bottom_mm: _Optional[float] = None,
    margin_top_mm: _Optional[float] = None,
    space_w_mm: _Optional[float] = None,
    space_h_mm: _Optional[float] = None,
    # Style parameters
    style: _Optional[_Dict[str, _Any]] = None,
    apply_style_mm: bool = True,
    # Panel labels (None = use style default, True/False = explicit)
    panel_labels: _Optional[bool] = None,
    **kwargs,
) -> _Tuple[_RecordingFigure, _Union[_RecordingAxes, _NDArray]]:
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
    fig: _Union[_RecordingFigure, _Figure],
    path: _Union[str, _Path],
    include_data: bool = True,
    data_format: _DataFormat = "csv",
    csv_format: _CsvFormat = "separate",
    validate: bool = True,
    validate_mse_threshold: float = 100.0,
    validate_error_level: str = "error",
    verbose: bool = True,
    dpi: _Optional[int] = None,
    image_format: _Optional[str] = None,
    background: _Optional[str] = None,
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
    csv_format : str
        CSV file structure: 'separate' (default) or 'single'.
        - 'separate': One CSV file per variable
        - 'single': Single CSV with all columns (scitex/SigmaPlot-compatible)
        Only applies when data_format='csv'.
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
    background : str, optional
        Background color (e.g., 'white', '#ffffff').
        If None, uses fig.set_background() value or style default.
        Use 'transparent' for transparent background.

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
        csv_format=csv_format,
        validate=validate,
        validate_mse_threshold=validate_mse_threshold,
        validate_error_level=validate_error_level,
        verbose=verbose,
        dpi=dpi,
        image_format=image_format,
        background=background,
    )


def reproduce(
    path: _Union[str, _Path],
    calls: _Optional[_List[str]] = None,
    skip_decorations: bool = False,
) -> _Tuple[_Figure, _Union[_Axes, _List[_Axes]]]:
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


def info(path: _Union[str, _Path]) -> _Dict[str, _Any]:
    """Get information about a recipe without reproducing."""
    return _get_recipe_info(path)


def _load_record(path: _Union[str, _Path]) -> _FigureRecord:
    """Load a recipe as a FigureRecord object (advanced use)."""
    return _load_recipe(path)


# Alias for intuitive save/load symmetry
load = reproduce


def extract_data(path: _Union[str, _Path]) -> _Dict[str, _Dict[str, _Any]]:
    """Extract data arrays from a saved recipe.

    Returns
    -------
    dict
        Nested dictionary: {call_id: {'x': array, 'y': array, ...}}
    """
    from ._api._extract import DECORATION_FUNCS, extract_call_data

    record = _load_recipe(path)
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
    path: _Union[str, _Path],
    mse_threshold: float = 100.0,
) -> _ValidationResult:
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
    working_dir=None,
    desktop: bool = False,
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
    working_dir : str or Path, optional
        Working directory for file browser (default: directory containing source).
    desktop : bool, optional
        Launch as native desktop window using pywebview (default: False).
        Requires: pip install figrecipe[desktop]

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
        working_dir=working_dir,
        desktop=desktop,
    )

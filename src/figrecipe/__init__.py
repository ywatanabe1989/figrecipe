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
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ._recorder import Recorder, FigureRecord, CallRecord
from ._wrappers import RecordingAxes, RecordingFigure
from ._wrappers._figure import create_recording_subplots
from ._serializer import save_recipe, load_recipe, recipe_to_dict
from ._reproducer import reproduce as _reproduce, get_recipe_info
from ._utils._numpy_io import DataFormat
from ._utils._units import mm_to_inch, mm_to_pt, inch_to_mm, pt_to_mm, normalize_color
from .styles._style_applier import list_available_fonts, check_font

# Lazy import for seaborn to avoid hard dependency
_sns_recorder = None


def _get_sns():
    """Get the seaborn recorder (lazy initialization)."""
    global _sns_recorder
    if _sns_recorder is None:
        from ._seaborn import get_seaborn_recorder
        _sns_recorder = get_seaborn_recorder()
    return _sns_recorder


class _SeabornProxy:
    """Proxy object for seaborn access via ps.sns."""

    def __getattr__(self, name: str):
        return getattr(_get_sns(), name)


# Create seaborn proxy
sns = _SeabornProxy()

__version__ = "0.4.0"
__all__ = [
    # Main API
    "subplots",
    "save",
    "reproduce",
    "info",
    "load",
    "extract_data",
    "validate",
    # Style system
    "load_style",
    "list_presets",
    "STYLE",
    "apply_style",
    # Unit conversions
    "mm_to_inch",
    "mm_to_pt",
    "inch_to_mm",
    "pt_to_mm",
    "normalize_color",
    # Font utilities
    "list_available_fonts",
    "check_font",
    # Seaborn support
    "sns",
    # Classes (for type hints)
    "RecordingFigure",
    "RecordingAxes",
    "FigureRecord",
    "CallRecord",
    "ValidationResult",
    # Version
    "__version__",
]


# Lazy imports for style system
_style_cache = None


def load_style(style=None):
    """Load style configuration from preset or YAML file.

    Parameters
    ----------
    style : str or Path, optional
        One of:
        - Preset name: "SCIENTIFIC", "MINIMAL", "PRESENTATION"
        - Path to custom YAML file: "/path/to/my_style.yaml"
        - None: uses default SCIENTIFIC preset

    Returns
    -------
    DotDict
        Style configuration with dot-notation access.

    Examples
    --------
    >>> import figrecipe as ps

    >>> # Load default (SCIENTIFIC preset)
    >>> style = ps.load_style()

    >>> # Load a specific preset
    >>> style = ps.load_style("MINIMAL")
    >>> style = ps.load_style("PRESENTATION")

    >>> # Load custom YAML file
    >>> style = ps.load_style("/path/to/my_style.yaml")

    >>> # Access style values
    >>> style.axes.width_mm
    40
    >>> style.colors.palette
    ['#0072B2', '#D55E00', ...]

    >>> # Use with subplots
    >>> fig, ax = ps.subplots(**style.to_subplots_kwargs())
    """
    from .styles import load_style as _load_style
    return _load_style(style)


def list_presets():
    """List available style presets.

    Returns
    -------
    list of str
        Names of available presets.

    Examples
    --------
    >>> import figrecipe as ps
    >>> ps.list_presets()
    ['MINIMAL', 'PRESENTATION', 'SCIENTIFIC']
    """
    from .styles import list_presets as _list_presets
    return _list_presets()


def apply_style(ax, style=None):
    """Apply mm-based styling to an axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes to apply styling to.
    style : dict or DotDict, optional
        Style configuration. If None, uses default FIGRECIPE_STYLE.

    Returns
    -------
    float
        Trace line width in points.

    Examples
    --------
    >>> import figrecipe as ps
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> trace_lw = ps.apply_style(ax)
    >>> ax.plot(x, y, lw=trace_lw)
    """
    from .styles import apply_style_mm, get_style, to_subplots_kwargs
    if style is None:
        style = to_subplots_kwargs(get_style())
    elif hasattr(style, 'to_subplots_kwargs'):
        style = style.to_subplots_kwargs()
    return apply_style_mm(ax, style)


class _StyleProxy:
    """Proxy object for lazy style loading."""

    def __getattr__(self, name):
        from .styles import STYLE
        return getattr(STYLE, name)

    def to_subplots_kwargs(self):
        from .styles import to_subplots_kwargs
        return to_subplots_kwargs()


STYLE = _StyleProxy()


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
    apply_style_mm: bool = False,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, List[RecordingAxes]]]:
    """Create a figure with recording-enabled axes.

    This is a drop-in replacement for plt.subplots() that wraps the
    returned figure and axes with recording capabilities.

    Supports mm-based layout control for publication-quality figures.

    Parameters
    ----------
    nrows : int
        Number of rows of subplots.
    ncols : int
        Number of columns of subplots.

    MM-Control Parameters
    ---------------------
    axes_width_mm : float, optional
        Axes width in mm. If provided, overrides figsize.
    axes_height_mm : float, optional
        Axes height in mm.
    margin_left_mm : float, optional
        Left margin in mm (default: 15).
    margin_right_mm : float, optional
        Right margin in mm (default: 5).
    margin_bottom_mm : float, optional
        Bottom margin in mm (default: 12).
    margin_top_mm : float, optional
        Top margin in mm (default: 8).
    space_w_mm : float, optional
        Horizontal spacing between axes in mm (default: 8).
    space_h_mm : float, optional
        Vertical spacing between axes in mm (default: 10).

    Style Parameters
    ----------------
    style : dict, optional
        Style configuration dictionary or result of load_style().
    apply_style_mm : bool
        If True, apply FIGRECIPE_STYLE to axes after creation.

    **kwargs
        Additional arguments passed to plt.subplots() (e.g., figsize, dpi).

    Returns
    -------
    fig : RecordingFigure
        Wrapped figure object.
    axes : RecordingAxes or list of RecordingAxes
        Wrapped axes (single for 1x1, list otherwise).

    Examples
    --------
    Basic usage:

    >>> import figrecipe as ps
    >>> fig, ax = ps.subplots()
    >>> ax.plot([1, 2, 3], [4, 5, 6], color='blue')
    >>> ps.save(fig, 'simple.yaml')

    MM-based layout:

    >>> fig, ax = ps.subplots(
    ...     axes_width_mm=40,
    ...     axes_height_mm=28,
    ...     margin_left_mm=15,
    ...     margin_bottom_mm=12,
    ... )

    With style:

    >>> style = ps.load_style()
    >>> fig, ax = ps.subplots(**style.to_subplots_kwargs())
    """
    # Check if mm-based layout is requested
    use_mm_layout = any([
        axes_width_mm is not None,
        axes_height_mm is not None,
        margin_left_mm is not None,
        margin_right_mm is not None,
        margin_bottom_mm is not None,
        margin_top_mm is not None,
        space_w_mm is not None,
        space_h_mm is not None,
    ])

    if use_mm_layout and 'figsize' not in kwargs:
        # Calculate figsize from mm parameters
        aw = axes_width_mm if axes_width_mm is not None else 40
        ah = axes_height_mm if axes_height_mm is not None else 28
        ml = margin_left_mm if margin_left_mm is not None else 15
        mr = margin_right_mm if margin_right_mm is not None else 5
        mb = margin_bottom_mm if margin_bottom_mm is not None else 12
        mt = margin_top_mm if margin_top_mm is not None else 8
        sw = space_w_mm if space_w_mm is not None else 8
        sh = space_h_mm if space_h_mm is not None else 10

        # Calculate total figure size
        total_width_mm = ml + (ncols * aw) + ((ncols - 1) * sw) + mr
        total_height_mm = mb + (nrows * ah) + ((nrows - 1) * sh) + mt

        # Convert to inches and set figsize
        kwargs['figsize'] = (mm_to_inch(total_width_mm), mm_to_inch(total_height_mm))

        # Store mm metadata for recording (will be extracted by create_recording_subplots)
        mm_layout = {
            'axes_width_mm': aw,
            'axes_height_mm': ah,
            'margin_left_mm': ml,
            'margin_right_mm': mr,
            'margin_bottom_mm': mb,
            'margin_top_mm': mt,
            'space_w_mm': sw,
            'space_h_mm': sh,
        }
    else:
        mm_layout = None

    # Handle style parameter
    if style is not None:
        if hasattr(style, 'to_subplots_kwargs'):
            # Merge style kwargs (style values are overridden by explicit params)
            style_kwargs = style.to_subplots_kwargs()
            for key, value in style_kwargs.items():
                if key not in kwargs:
                    kwargs[key] = value

    # Create the recording subplots
    fig, axes = create_recording_subplots(nrows, ncols, **kwargs)

    # Store mm_layout metadata on figure for serialization
    if mm_layout is not None:
        fig._mm_layout = mm_layout

        # Apply subplots_adjust to position axes correctly
        total_width_mm = ml + (ncols * aw) + ((ncols - 1) * sw) + mr
        total_height_mm = mb + (nrows * ah) + ((nrows - 1) * sh) + mt

        # Calculate relative positions (0-1 range)
        left = ml / total_width_mm
        right = 1 - (mr / total_width_mm)
        bottom = mb / total_height_mm
        top = 1 - (mt / total_height_mm)

        # Calculate spacing as fraction of figure size
        wspace = sw / aw if ncols > 1 else 0
        hspace = sh / ah if nrows > 1 else 0

        fig.fig.subplots_adjust(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            wspace=wspace,
            hspace=hspace,
        )

        # Record layout in figure record for reproduction
        fig.record.layout = {
            'left': left,
            'right': right,
            'bottom': bottom,
            'top': top,
            'wspace': wspace,
            'hspace': hspace,
        }

    # Apply styling if requested
    style_dict = None
    if apply_style_mm or style is not None:
        from .styles import apply_style_mm as _apply_style, to_subplots_kwargs, get_style
        style_dict = to_subplots_kwargs(get_style()) if style is None else (
            style.to_subplots_kwargs() if hasattr(style, 'to_subplots_kwargs') else style
        )
        if nrows == 1 and ncols == 1:
            _apply_style(axes._ax, style_dict)
        else:
            # Handle 2D array of axes
            import numpy as np
            axes_array = np.array(axes)
            for ax in axes_array.flat:
                _apply_style(ax._ax if hasattr(ax, '_ax') else ax, style_dict)

        # Record style in figure record for reproduction
        fig.record.style = style_dict

    return fig, axes


def save(
    fig: Union[RecordingFigure, Figure],
    path: Union[str, Path],
    include_data: bool = True,
    data_format: DataFormat = "csv",
    validate: bool = True,
    validate_mse_threshold: float = 100.0,
):
    """Save a figure's recipe to file.

    Parameters
    ----------
    fig : RecordingFigure or Figure
        The figure to save. Must be a RecordingFigure for recipe saving.
    path : str or Path
        Output path. Use .yaml extension for recipe format.
    include_data : bool
        If True, save large arrays to separate files.
    data_format : str
        Format for data files: 'csv' (default), 'npz', or 'inline'.
        - 'csv': Human-readable CSV files with dtype header
        - 'npz': Compressed numpy binary format (efficient)
        - 'inline': Store all data directly in YAML
    validate : bool
        If True (default), validate reproducibility after saving by
        reproducing the figure and comparing it to the original.
    validate_mse_threshold : float
        Maximum acceptable MSE for validation (default: 100).

    Returns
    -------
    Path or tuple
        If validate=False: Path to saved file.
        If validate=True: (Path, ValidationResult) tuple.

    Examples
    --------
    >>> import figrecipe as ps
    >>> fig, ax = ps.subplots()
    >>> ax.plot(x, y, color='red', id='my_data')
    >>> ps.save(fig, 'experiment.yaml')  # Uses CSV (default)
    >>> ps.save(fig, 'experiment.yaml', data_format='npz')  # Binary
    >>>
    >>> # With validation
    >>> path, result = ps.save(fig, 'experiment.yaml', validate=True)
    >>> print(result.summary())

    Notes
    -----
    The recipe file contains:
    - Figure metadata (size, DPI, matplotlib version)
    - All plotting calls with their arguments
    - References to data files for large arrays
    """
    path = Path(path)

    if isinstance(fig, RecordingFigure):
        saved_path = fig.save_recipe(path, include_data=include_data, data_format=data_format)

        if validate:
            from ._validator import validate_on_save
            result = validate_on_save(fig, saved_path, mse_threshold=validate_mse_threshold)
            status = "PASSED" if result.valid else "FAILED"
            print(f"Saved: {saved_path} (Validation: {status})")
            return saved_path, result

        print(f"Saved: {saved_path}")
        return saved_path
    else:
        raise TypeError(
            "Expected RecordingFigure. Use ps.subplots() to create "
            "a recording-enabled figure."
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
        If True, skip decoration calls (labels, legends, etc.).

    Returns
    -------
    fig : matplotlib.figure.Figure
        Reproduced figure.
    axes : Axes or list of Axes
        Reproduced axes.

    Examples
    --------
    >>> import figrecipe as ps
    >>> fig, ax = ps.reproduce('experiment.yaml')
    >>> plt.show()

    >>> # Reproduce only specific plots
    >>> fig, ax = ps.reproduce('experiment.yaml', calls=['scatter_001'])
    """
    return _reproduce(path, calls=calls, skip_decorations=skip_decorations)


def info(path: Union[str, Path]) -> Dict[str, Any]:
    """Get information about a recipe without reproducing.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    dict
        Recipe information including figure ID, creation time,
        matplotlib version, size, and list of calls.

    Examples
    --------
    >>> import figrecipe as ps
    >>> recipe_info = ps.info('experiment.yaml')
    >>> print(f"Created: {recipe_info['created']}")
    >>> print(f"Calls: {len(recipe_info['calls'])}")
    """
    return get_recipe_info(path)


def load(path: Union[str, Path]) -> FigureRecord:
    """Load a recipe as a FigureRecord object.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    FigureRecord
        The loaded figure record.

    Examples
    --------
    >>> import figrecipe as ps
    >>> record = ps.load('experiment.yaml')
    >>> # Modify the record
    >>> record.axes['ax_0_0'].calls[0].kwargs['color'] = 'blue'
    >>> # Reproduce with modifications
    >>> fig, ax = ps.reproduce_from_record(record)
    """
    return load_recipe(path)


def extract_data(path: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
    """Extract data arrays from a saved recipe.

    This function allows you to import/recover the data that was
    plotted in a figure from its recipe file.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    dict
        Nested dictionary: {call_id: {'x': array, 'y': array, ...}}
        Each call's data is stored under its ID with keys for each argument.

    Examples
    --------
    >>> import figrecipe as ps
    >>> import numpy as np
    >>>
    >>> # Create and save a figure
    >>> x = np.linspace(0, 10, 100)
    >>> y = np.sin(x)
    >>> fig, ax = ps.subplots()
    >>> ax.plot(x, y, id='sine_wave')
    >>> ps.save(fig, 'figure.yaml')
    >>>
    >>> # Later, extract the data
    >>> data = ps.extract_data('figure.yaml')
    >>> x_recovered = data['sine_wave']['x']
    >>> y_recovered = data['sine_wave']['y']
    >>> np.allclose(x, x_recovered)
    True

    Notes
    -----
    - Data is extracted from all plot calls (plot, scatter, bar, etc.)
    - For plot() calls: 'x' and 'y' contain the coordinates
    - For scatter(): 'x', 'y', and optionally 'c' (colors), 's' (sizes)
    - For bar(): 'x' (categories) and 'height' (values)
    - For hist(): 'x' (data array)
    """
    import numpy as np

    record = load_recipe(path)
    result = {}

    # Decoration functions to skip
    decoration_funcs = {
        "set_xlabel", "set_ylabel", "set_title", "set_xlim", "set_ylim",
        "legend", "grid", "axhline", "axvline", "text", "annotate",
    }

    for ax_key, ax_record in record.axes.items():
        for call in ax_record.calls:
            # Skip decoration calls
            if call.function in decoration_funcs:
                continue

            call_data = {}

            def to_array(data):
                """Convert data to numpy array, handling YAML types."""
                # Handle dict with 'data' key (serialized array format)
                if isinstance(data, dict) or (hasattr(data, "keys") and "data" in data):
                    return np.array(data["data"])
                if hasattr(data, "tolist"):  # Already array-like
                    return np.array(data)
                return np.array(list(data) if hasattr(data, "__iter__") and not isinstance(data, str) else data)

            # Extract positional arguments based on function type
            if call.function in ("plot", "scatter", "fill_between"):
                if len(call.args) >= 1:
                    call_data["x"] = to_array(call.args[0])
                if len(call.args) >= 2:
                    call_data["y"] = to_array(call.args[1])

            elif call.function == "bar":
                if len(call.args) >= 1:
                    call_data["x"] = to_array(call.args[0])
                if len(call.args) >= 2:
                    call_data["height"] = to_array(call.args[1])

            elif call.function == "hist":
                if len(call.args) >= 1:
                    call_data["x"] = to_array(call.args[0])

            elif call.function == "errorbar":
                if len(call.args) >= 1:
                    call_data["x"] = to_array(call.args[0])
                if len(call.args) >= 2:
                    call_data["y"] = to_array(call.args[1])

            # Extract relevant kwargs
            for key in ("c", "s", "yerr", "xerr", "weights", "bins"):
                if key in call.kwargs:
                    val = call.kwargs[key]
                    if isinstance(val, (list, tuple)) or hasattr(val, "__iter__") and not isinstance(val, str):
                        call_data[key] = to_array(val)
                    else:
                        call_data[key] = val

            if call_data:
                result[call.id] = call_data

    return result


# Import ValidationResult for type hints
from ._validator import ValidationResult, validate_recipe


def validate(
    path: Union[str, Path],
    mse_threshold: float = 100.0,
) -> ValidationResult:
    """Validate that a saved recipe can reproduce its original figure.

    This is a standalone validation function for existing recipes.
    For validation during save, use `ps.save(..., validate=True)`.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.
    mse_threshold : float
        Maximum acceptable MSE for validation to pass (default: 100).

    Returns
    -------
    ValidationResult
        Detailed comparison results including MSE, dimensions, etc.

    Examples
    --------
    >>> import figrecipe as ps
    >>> result = ps.validate('experiment.yaml')
    >>> print(result.summary())
    >>> if result.valid:
    ...     print("Recipe is reproducible!")

    Notes
    -----
    This function reproduces the figure from the recipe and compares
    the result to re-rendering the recipe. It cannot compare to the
    original figure unless you use `ps.save(..., validate=True)` which
    performs validation before closing the original figure.
    """
    # For standalone validation, we reproduce twice and compare
    # (This validates the recipe is self-consistent)
    from ._reproducer import reproduce
    from ._utils._image_diff import compare_images
    import tempfile
    import numpy as np

    path = Path(path)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Reproduce twice
        fig1, _ = reproduce(path)
        img1_path = tmpdir / "render1.png"
        fig1.savefig(img1_path, dpi=150)

        fig2, _ = reproduce(path)
        img2_path = tmpdir / "render2.png"
        fig2.savefig(img2_path, dpi=150)

        # Compare
        diff = compare_images(img1_path, img2_path)

        mse = diff["mse"]
        if np.isnan(mse):
            valid = False
            message = f"Image dimensions differ: {diff['size1']} vs {diff['size2']}"
        elif mse > mse_threshold:
            valid = False
            message = f"MSE ({mse:.2f}) exceeds threshold ({mse_threshold})"
        else:
            valid = True
            message = "Recipe produces consistent output"

        return ValidationResult(
            valid=valid,
            mse=mse if not np.isnan(mse) else float("inf"),
            psnr=diff["psnr"],
            max_diff=diff["max_diff"] if not np.isnan(diff["max_diff"]) else float("inf"),
            size_original=diff["size1"],
            size_reproduced=diff["size2"],
            same_size=diff["same_size"],
            file_size_diff=diff["file_size2"] - diff["file_size1"],
            message=message,
        )

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
from ._utils._units import mm_to_inch, mm_to_pt, inch_to_mm, pt_to_mm, mm_to_scatter_size, normalize_color
from .styles._style_applier import list_available_fonts, check_font

# Notebook display format flag (set once per session)
_notebook_format_set = False


def _enable_notebook_svg():
    """Enable SVG format for Jupyter notebook display.

    This provides crisp vector graphics at any zoom level.
    Called automatically when load_style() or subplots() is used.
    """
    global _notebook_format_set
    if _notebook_format_set:
        return

    try:
        # Method 1: matplotlib_inline (IPython 7.0+, JupyterLab)
        from matplotlib_inline.backend_inline import set_matplotlib_formats
        set_matplotlib_formats('svg')
        _notebook_format_set = True
    except (ImportError, Exception):
        try:
            # Method 2: IPython config (older IPython)
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython is not None and hasattr(ipython, 'kernel'):
                # Only run in actual Jupyter kernel, not IPython console
                ipython.run_line_magic('config', "InlineBackend.figure_formats = ['svg']")
                _notebook_format_set = True
        except Exception:
            pass  # Not in Jupyter environment or method not available


def enable_svg():
    """Manually enable SVG format for Jupyter notebook display.

    Call this if figures appear pixelated in notebooks.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fr.enable_svg()  # Enable SVG rendering
    >>> fig, ax = fr.subplots()  # Now renders as crisp SVG
    """
    global _notebook_format_set
    _notebook_format_set = False  # Force re-application
    _enable_notebook_svg()


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
    # Version
    "__version__",
]


# Lazy imports for style system
_style_cache = None


def load_style(style="SCITEX", dark=False):
    """Load style configuration and apply it globally.

    After calling this function, subsequent `subplots()` calls will
    automatically use the loaded style (fonts, colors, theme, etc.).

    Parameters
    ----------
    style : str, Path, bool, or None
        One of:
        - "SCITEX" / "FIGRECIPE": Scientific publication style (default)
        - "MATPLOTLIB": Vanilla matplotlib defaults
        - Path to custom YAML file: "/path/to/my_style.yaml"
        - None or False: Unload style (reset to matplotlib defaults)
    dark : bool, optional
        If True, apply dark theme transformation (default: False).
        Equivalent to appending "_DARK" to preset name.

    Returns
    -------
    DotDict or None
        Style configuration with dot-notation access.
        Returns None if style is unloaded.

    Examples
    --------
    >>> import figrecipe as fr

    >>> # Load scientific style (default)
    >>> fr.load_style()
    >>> fr.load_style("SCITEX")  # explicit

    >>> # Load dark theme
    >>> fr.load_style("SCITEX_DARK")
    >>> fr.load_style("SCITEX", dark=True)  # equivalent

    >>> # Reset to vanilla matplotlib
    >>> fr.load_style(None)    # unload
    >>> fr.load_style(False)   # unload
    >>> fr.load_style("MATPLOTLIB")  # explicit vanilla

    >>> # Access style values
    >>> style = fr.load_style("SCITEX")
    >>> style.axes.width_mm
    40
    """
    from .styles import load_style as _load_style
    return _load_style(style, dark=dark)


def unload_style():
    """Unload the current style and reset to matplotlib defaults.

    After calling this, subsequent `subplots()` calls will use vanilla
    matplotlib behavior without FigRecipe styling.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fr.load_style("SCITEX")  # Apply scientific style
    >>> fig, ax = fr.subplots()  # Styled
    >>> fr.unload_style()        # Reset to matplotlib defaults
    >>> fig, ax = fr.subplots()  # Vanilla matplotlib
    """
    from .styles import unload_style as _unload_style
    _unload_style()


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
    apply_style_mm: bool = True,
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
        If True (default), apply loaded style to axes after creation.
        Set to False to disable automatic style application.

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

    With style (automatically applied):

    >>> ps.load_style("FIGRECIPE_DARK")  # Load dark theme
    >>> fig, ax = ps.subplots()  # Style applied automatically
    """
    # Get global style for default values (if loaded)
    from .styles._style_loader import _STYLE_CACHE
    global_style = _STYLE_CACHE

    # Helper to get value with priority: explicit > global style > hardcoded default
    def _get_mm(explicit, style_path, default):
        if explicit is not None:
            return explicit
        if global_style is not None:
            try:
                val = global_style
                for key in style_path:
                    val = val.get(key) if isinstance(val, dict) else getattr(val, key, None)
                    if val is None:
                        break
                if val is not None:
                    return val
            except (KeyError, AttributeError):
                pass
        return default

    # Check if mm-based layout is requested (explicit OR from global style)
    has_explicit_mm = any([
        axes_width_mm is not None,
        axes_height_mm is not None,
        margin_left_mm is not None,
        margin_right_mm is not None,
        margin_bottom_mm is not None,
        margin_top_mm is not None,
        space_w_mm is not None,
        space_h_mm is not None,
    ])

    # Also use mm layout if global style has mm values
    has_style_mm = False
    if global_style is not None:
        try:
            has_style_mm = (
                global_style.get('axes', {}).get('width_mm') is not None or
                getattr(getattr(global_style, 'axes', None), 'width_mm', None) is not None
            )
        except (KeyError, AttributeError):
            pass

    use_mm_layout = has_explicit_mm or has_style_mm

    if use_mm_layout and 'figsize' not in kwargs:
        # Get mm values: explicit params > global style > hardcoded defaults
        aw = _get_mm(axes_width_mm, ['axes', 'width_mm'], 40)
        ah = _get_mm(axes_height_mm, ['axes', 'height_mm'], 28)
        ml = _get_mm(margin_left_mm, ['margins', 'left_mm'], 15)
        mr = _get_mm(margin_right_mm, ['margins', 'right_mm'], 5)
        mb = _get_mm(margin_bottom_mm, ['margins', 'bottom_mm'], 12)
        mt = _get_mm(margin_top_mm, ['margins', 'top_mm'], 8)
        sw = _get_mm(space_w_mm, ['spacing', 'horizontal_mm'], 8)
        sh = _get_mm(space_h_mm, ['spacing', 'vertical_mm'], 10)

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

    # Apply DPI from global style if not explicitly provided
    if 'dpi' not in kwargs and global_style is not None:
        # Try figure.dpi first, then output.dpi
        style_dpi = None
        try:
            if hasattr(global_style, 'figure') and hasattr(global_style.figure, 'dpi'):
                style_dpi = global_style.figure.dpi
            elif hasattr(global_style, 'output') and hasattr(global_style.output, 'dpi'):
                style_dpi = global_style.output.dpi
        except (KeyError, AttributeError):
            pass
        if style_dpi is not None:
            kwargs['dpi'] = style_dpi

    # Handle style parameter
    if style is not None:
        if hasattr(style, 'to_subplots_kwargs'):
            # Merge style kwargs (style values are overridden by explicit params)
            style_kwargs = style.to_subplots_kwargs()
            for key, value in style_kwargs.items():
                if key not in kwargs:
                    kwargs[key] = value

    # Use constrained_layout by default for non-mm layouts (better auto-spacing)
    # Don't use it with mm-based layout since we manually control positioning
    if not use_mm_layout and 'constrained_layout' not in kwargs:
        kwargs['constrained_layout'] = True

    # Create the recording subplots
    fig, axes = create_recording_subplots(nrows, ncols, **kwargs)

    # Record constrained_layout setting for reproduction
    fig.record.constrained_layout = kwargs.get('constrained_layout', False)

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

    # Apply styling if requested and a style is actually loaded
    style_dict = None
    should_apply_style = False

    if style is not None:
        # Explicit style parameter provided
        should_apply_style = True
        style_dict = style.to_subplots_kwargs() if hasattr(style, 'to_subplots_kwargs') else style
    elif apply_style_mm and global_style is not None:
        # Use global style if loaded and has meaningful values (not MATPLOTLIB)
        from .styles import to_subplots_kwargs
        style_dict = to_subplots_kwargs(global_style)
        # Only apply if style has essential mm values (skip MATPLOTLIB which has all None)
        if style_dict and style_dict.get('axes_thickness_mm') is not None:
            should_apply_style = True

    if should_apply_style and style_dict:
        from .styles import apply_style_mm as _apply_style
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
        The figure to save. Must be a RecordingFigure for recipe saving.
    path : str or Path
        Output path. Can be:
        - Image path (.png, .pdf, .svg, .jpg): Saves image + YAML recipe
        - YAML path (.yaml, .yml): Saves recipe + image
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
    validate_error_level : str
        How to handle validation failures: 'error' (default), 'warning', or 'debug'.
        - 'error': Raise ValueError on failure
        - 'warning': Emit UserWarning on failure
        - 'debug': Silent (check result.valid manually)
    verbose : bool
        If True (default), print save status. Set False for CI/scripts.
    dpi : int, optional
        DPI for image output. Uses style DPI or 300 if not specified.
    image_format : str, optional
        Image format when path is YAML ('png', 'pdf', 'svg').
        Uses style's output.format or 'png' if not specified.

    Returns
    -------
    tuple
        (image_path, yaml_path, ValidationResult or None) tuple.
        ValidationResult is None when validate=False.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot(x, y, color='red', id='my_data')
    >>>
    >>> # Save as PNG (also creates experiment.yaml)
    >>> img_path, yaml_path, result = fr.save(fig, 'experiment.png')
    >>>
    >>> # Save as YAML (also creates experiment.png)
    >>> img_path, yaml_path, result = fr.save(fig, 'experiment.yaml')
    >>>
    >>> # Save as PDF with custom DPI
    >>> fr.save(fig, 'experiment.pdf', dpi=600)

    Notes
    -----
    The recipe file contains:
    - Figure metadata (size, DPI, matplotlib version)
    - All plotting calls with their arguments
    - References to data files for large arrays
    """
    path = Path(path)

    if not isinstance(fig, RecordingFigure):
        raise TypeError(
            "Expected RecordingFigure. Use fr.subplots() to create "
            "a recording-enabled figure."
        )

    # Determine image and YAML paths based on extension
    IMAGE_EXTENSIONS = {'.png', '.pdf', '.svg', '.jpg', '.jpeg', '.eps', '.tiff', '.tif'}
    YAML_EXTENSIONS = {'.yaml', '.yml'}

    suffix_lower = path.suffix.lower()

    if suffix_lower in IMAGE_EXTENSIONS:
        # User provided image path
        image_path = path
        yaml_path = path.with_suffix('.yaml')
        img_format = suffix_lower[1:]  # Remove leading dot
    elif suffix_lower in YAML_EXTENSIONS:
        # User provided YAML path
        yaml_path = path
        # Determine image format from style or default
        if image_format is not None:
            img_format = image_format.lower().lstrip('.')
        else:
            # Check global style for preferred format
            from .styles._style_loader import _STYLE_CACHE
            if _STYLE_CACHE is not None:
                try:
                    img_format = _STYLE_CACHE.output.format.lower()
                except (KeyError, AttributeError):
                    img_format = 'png'
            else:
                img_format = 'png'
        image_path = path.with_suffix(f'.{img_format}')
    else:
        # Unknown extension - treat as base name, add both extensions
        yaml_path = path.with_suffix('.yaml')
        if image_format is not None:
            img_format = image_format.lower().lstrip('.')
        else:
            from .styles._style_loader import _STYLE_CACHE
            if _STYLE_CACHE is not None:
                try:
                    img_format = _STYLE_CACHE.output.format.lower()
                except (KeyError, AttributeError):
                    img_format = 'png'
            else:
                img_format = 'png'
        image_path = path.with_suffix(f'.{img_format}')

    # Get DPI from style if not specified
    if dpi is None:
        from .styles._style_loader import _STYLE_CACHE
        if _STYLE_CACHE is not None:
            try:
                dpi = _STYLE_CACHE.output.dpi
            except (KeyError, AttributeError):
                dpi = 300
        else:
            dpi = 300

    # Get transparency setting from style
    transparent = False
    from .styles._style_loader import _STYLE_CACHE
    if _STYLE_CACHE is not None:
        try:
            transparent = _STYLE_CACHE.output.transparent
        except (KeyError, AttributeError):
            pass

    # Save the image
    fig.fig.savefig(image_path, dpi=dpi, bbox_inches='tight', transparent=transparent)

    # Save the recipe
    saved_yaml = fig.save_recipe(yaml_path, include_data=include_data, data_format=data_format)

    # Validate if requested
    if validate:
        from ._validator import validate_on_save
        result = validate_on_save(fig, saved_yaml, mse_threshold=validate_mse_threshold)
        status = "PASSED" if result.valid else "FAILED"
        if verbose:
            print(f"Saved: {image_path} + {yaml_path} (Reproducible Validation: {status})")
        if not result.valid:
            msg = f"Reproducibility validation failed (MSE={result.mse:.1f}): {result.message}"
            if validate_error_level == "error":
                raise ValueError(msg)
            elif validate_error_level == "warning":
                import warnings
                warnings.warn(msg, UserWarning)
            # "debug" level: silent, just return the result
        return image_path, yaml_path, result

    if verbose:
        print(f"Saved: {image_path} + {yaml_path}")
    return image_path, yaml_path, None


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


def crop(input_path, output_path=None, margin_mm=1.0, margin_px=None, overwrite=False, verbose=False):
    """Crop a figure image to its content area with a specified margin.

    Automatically detects background color (from corners) and crops to
    content, leaving only the specified margin around it.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image (PNG, JPEG, etc.)
    output_path : str or Path, optional
        Path to save the cropped image. If None and overwrite=True,
        overwrites the input. If None and overwrite=False, adds '_cropped' suffix.
    margin_mm : float, optional
        Margin in millimeters to keep around content (default: 1.0mm).
        Converted to pixels using image DPI (or 300 DPI if not available).
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

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots(axes_width_mm=60, axes_height_mm=40)
    >>> ax.plot([1, 2, 3], [1, 2, 3], id='line')
    >>> fig.savefig("figure.png", dpi=300)
    >>> fr.crop("figure.png", overwrite=True)  # 1mm margin
    >>> fr.crop("figure.png", margin_mm=2.0)   # 2mm margin
    """
    from ._utils._crop import crop as _crop
    return _crop(input_path, output_path, margin_mm, margin_px, overwrite, verbose)

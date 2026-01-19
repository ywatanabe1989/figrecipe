#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main composition logic for combining multiple figures."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from numpy.typing import NDArray

from .._recorder import FigureRecord
from .._serializer import load_recipe
from .._wrappers import RecordingAxes, RecordingFigure

# Supported image file extensions for raw image composition
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".webp"}
# SVG requires special handling (vector format)
VECTOR_EXTENSIONS = {".svg"}


def _is_image_file(path: Path) -> bool:
    """Check if path is a supported image file.

    Parameters
    ----------
    path : Path
        File path to check.

    Returns
    -------
    bool
        True if path is a supported image file.
    """
    suffix = path.suffix.lower()
    return suffix in IMAGE_EXTENSIONS or suffix in VECTOR_EXTENSIONS


def _create_image_record(image_path: Path) -> FigureRecord:
    """Create a FigureRecord from a raw image file.

    The record contains a single axes with an imshow() call displaying the image.
    Axis ticks and labels are turned off for clean image display.

    Parameters
    ----------
    image_path : Path
        Path to the image file.

    Returns
    -------
    FigureRecord
        A figure record with the image displayed via imshow().
    """
    from datetime import datetime

    import matplotlib
    import numpy as np
    from PIL import Image

    from .._recorder import AxesRecord, CallRecord

    # Load image
    suffix = image_path.suffix.lower()
    if suffix == ".svg":
        # SVG requires special handling - convert to raster first
        try:
            import io

            import cairosvg

            png_data = cairosvg.svg2png(url=str(image_path))
            img = Image.open(io.BytesIO(png_data))
        except ImportError:
            raise ImportError(
                "cairosvg is required for SVG support. Install with: pip install cairosvg"
            )
    else:
        img = Image.open(image_path)

    # Convert to numpy array (RGB/RGBA)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img_array = np.array(img)

    # Create CallRecord for imshow
    imshow_call = CallRecord(
        id=f"imshow_{image_path.stem}",
        function="imshow",
        args=[{"name": "X", "dtype": "ndarray", "data": img_array.tolist()}],
        kwargs={"aspect": "equal"},
        timestamp=datetime.now().isoformat(),
        ax_position=(0, 0),
    )

    # Create decoration calls to turn off axis
    axis_off_call = CallRecord(
        id="axis_off",
        function="axis",
        args=[{"name": "arg0", "data": "off"}],
        kwargs={},
        timestamp=datetime.now().isoformat(),
        ax_position=(0, 0),
    )

    # Create AxesRecord
    ax_record = AxesRecord(
        position=(0, 0),
        calls=[imshow_call],
        decorations=[axis_off_call],
    )

    # Determine figure size based on image dimensions (in inches at 100 dpi)
    height, width = img_array.shape[:2]
    dpi = 100
    figsize = (width / dpi, height / dpi)

    # Create FigureRecord
    record = FigureRecord(
        figsize=figsize,
        dpi=dpi,
        matplotlib_version=matplotlib.__version__,
    )
    record.axes["ax_0_0"] = ax_record

    return record


def compose(
    layout: Tuple[int, int],
    sources: Dict[Tuple[int, int], Union[str, Path, FigureRecord, Tuple]],
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray]]:
    """Compose a new figure from multiple sources (recipes or raw images).

    Parameters
    ----------
    layout : tuple
        (nrows, ncols) for the new composite figure.
    sources : dict
        Mapping of (row, col) -> source specification.
        Source can be:
        - str/Path to .yaml recipe file (uses first axes)
        - str/Path to image file (.png, .jpg, .jpeg, .tiff, .bmp, .gif, .webp, .svg)
        - FigureRecord: Direct record (uses first axes)
        - Tuple[source, ax_key]: Specific axes from source

    **kwargs
        Additional arguments passed to subplots().

    Returns
    -------
    fig : RecordingFigure
        Composed figure.
    axes : RecordingAxes or ndarray of RecordingAxes
        Axes of the composed figure.

    Examples
    --------
    Compose from recipe files:

    >>> import figrecipe as fr
    >>> fig, axes = fr.compose(
    ...     layout=(1, 2),
    ...     sources={
    ...         (0, 0): "experiment_a.yaml",
    ...         (0, 1): "experiment_b.yaml",
    ...     }
    ... )

    Compose with mixed sources (recipes and raw images):

    >>> fig, axes = fr.compose(
    ...     layout=(1, 3),
    ...     sources={
    ...         (0, 0): "microscopy_image.png",  # Raw PNG image
    ...         (0, 1): "diagram.svg",            # Raw SVG image
    ...         (0, 2): "my_plot.yaml",           # Recipe file
    ...     }
    ... )

    Notes
    -----
    Raw image files are displayed using ``ax.imshow()`` with axis turned off.
    SVG files require the ``cairosvg`` package for rasterization.
    """
    from .. import subplots

    nrows, ncols = layout
    fig, axes = subplots(nrows=nrows, ncols=ncols, **kwargs)

    # Track source data directories for symlink support
    source_data_dirs = {}

    for (row, col), source_spec in sources.items():
        source_record, ax_key, source_path = _parse_source_spec_with_path(source_spec)
        ax_record = source_record.axes.get(ax_key)

        if ax_record is None:
            available = list(source_record.axes.keys())
            raise ValueError(
                f"Axes '{ax_key}' not found in source. Available: {available}"
            )

        target_ax = _get_axes_at(axes, row, col, nrows, ncols)
        _replay_axes_record(target_ax, ax_record, fig.record, row, col)

        # Track source data directory if source was a file path
        if source_path is not None:
            data_dir = source_path.parent / f"{source_path.stem}_data"
            if data_dir.exists():
                target_ax_key = f"ax_{row}_{col}"
                source_data_dirs[target_ax_key] = data_dir

    # Store source data directories on figure record for symlink support
    if source_data_dirs:
        fig.record.source_data_dirs = source_data_dirs

    return fig, axes


def _parse_source_spec(
    spec: Union[str, Path, FigureRecord, Tuple],
) -> Tuple[FigureRecord, str]:
    """Parse source specification into (FigureRecord, ax_key).

    Parameters
    ----------
    spec : various
        Source specification.

    Returns
    -------
    tuple
        (FigureRecord, ax_key)
    """
    record, ax_key, _ = _parse_source_spec_with_path(spec)
    return record, ax_key


def _parse_source_spec_with_path(
    spec: Union[str, Path, FigureRecord, Tuple],
) -> Tuple[FigureRecord, str, Optional[Path]]:
    """Parse source specification into (FigureRecord, ax_key, source_path).

    Parameters
    ----------
    spec : various
        Source specification. Can be:
        - str/Path to .yaml recipe file
        - str/Path to image file (.png, .jpg, .jpeg, .tiff, .bmp, .gif, .webp, .svg)
        - FigureRecord object
        - Tuple of (source, ax_key) for specific axes selection

    Returns
    -------
    tuple
        (FigureRecord, ax_key, source_path or None)
    """
    if isinstance(spec, (str, Path)):
        path = Path(spec)
        # Check if it's an image file
        if _is_image_file(path):
            return _create_image_record(path), "ax_0_0", path
        # Otherwise load as recipe
        return load_recipe(path), "ax_0_0", path
    elif isinstance(spec, FigureRecord):
        return spec, "ax_0_0", None
    elif isinstance(spec, tuple) and len(spec) == 2:
        source, ax_key = spec
        if isinstance(source, (str, Path)):
            path = Path(source)
            # Check if it's an image file
            if _is_image_file(path):
                return _create_image_record(path), "ax_0_0", path
            return load_recipe(path), ax_key, path
        elif isinstance(source, FigureRecord):
            return source, ax_key, None
        raise TypeError(f"Invalid source in tuple: {type(source)}")
    raise TypeError(f"Invalid source spec type: {type(spec)}")


def _get_axes_at(
    axes: Union[RecordingAxes, NDArray],
    row: int,
    col: int,
    nrows: int,
    ncols: int,
) -> RecordingAxes:
    """Get axes at position, handling different array shapes.

    Parameters
    ----------
    axes : RecordingAxes or ndarray
        Axes object(s) from subplots.
    row, col : int
        Target position.
    nrows, ncols : int
        Grid dimensions.

    Returns
    -------
    RecordingAxes
        Axes at the specified position.
    """
    if nrows == 1 and ncols == 1:
        return axes
    elif nrows == 1:
        return axes[col]
    elif ncols == 1:
        return axes[row]
    else:
        return axes[row, col]


def _replay_axes_record(
    target_ax: RecordingAxes,
    ax_record,
    fig_record: FigureRecord,
    row: int,
    col: int,
) -> None:
    """Replay all calls from ax_record onto target axes.

    Parameters
    ----------
    target_ax : RecordingAxes
        Target axes to replay onto.
    ax_record : AxesRecord
        Source axes record with calls.
    fig_record : FigureRecord
        Figure record to update.
    row, col : int
        Target position for recording.
    """
    from .._reproducer._core import _replay_call

    mpl_ax = target_ax._ax if hasattr(target_ax, "_ax") else target_ax
    result_cache: Dict[str, Any] = {}

    # Replay plotting calls
    for call in ax_record.calls:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    # Replay decoration calls
    for call in ax_record.decorations:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    # Update figure record with imported axes
    ax_key = f"ax_{row}_{col}"
    fig_record.axes[ax_key] = ax_record


__all__ = ["compose"]

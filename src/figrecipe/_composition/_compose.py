#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main composition logic for combining multiple figures.

Supports two composition modes:
1. Grid-based: layout=(nrows, ncols) with sources={(row, col): path}
2. Mm-based: canvas_size_mm=(w, h) with sources={path: {"xy_mm": ..., "size_mm": ...}}

All layouts maintain matplotlib editability - no PIL image pasting.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from numpy.typing import NDArray

from .._recorder import FigureRecord
from .._serializer import load_recipe
from .._wrappers import RecordingAxes, RecordingFigure

# Supported image file extensions for raw image composition
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".webp"}
# SVG requires special handling (vector format)
VECTOR_EXTENSIONS = {".svg"}

# Default DPI for mm-based composition
DEFAULT_DPI = 300


def _is_image_file(path: Path) -> bool:
    """Check if path is a supported image file."""
    suffix = path.suffix.lower()
    return suffix in IMAGE_EXTENSIONS or suffix in VECTOR_EXTENSIONS


def _is_mm_based_sources(sources: Dict) -> bool:
    """Check if sources dict uses mm-based positioning."""
    if not sources:
        return False
    first_key = next(iter(sources.keys()))
    # Grid-based uses tuple keys like (0, 0)
    if isinstance(first_key, tuple):
        return False
    # Mm-based uses string/Path keys with dict values containing xy_mm
    first_value = sources[first_key]
    return isinstance(first_value, dict) and "xy_mm" in first_value


def _mm_to_inch(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / 25.4


def _create_image_record(image_path: Path) -> FigureRecord:
    """Create a FigureRecord from a raw image file."""
    from datetime import datetime

    import matplotlib
    import numpy as np
    from PIL import Image

    from .._recorder import AxesRecord, CallRecord

    suffix = image_path.suffix.lower()
    if suffix == ".svg":
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

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img_array = np.array(img)

    imshow_call = CallRecord(
        id=f"imshow_{image_path.stem}",
        function="imshow",
        args=[{"name": "X", "dtype": "ndarray", "data": img_array.tolist()}],
        kwargs={"aspect": "equal"},
        timestamp=datetime.now().isoformat(),
        ax_position=(0, 0),
    )

    axis_off_call = CallRecord(
        id="axis_off",
        function="axis",
        args=[{"name": "arg0", "data": "off"}],
        kwargs={},
        timestamp=datetime.now().isoformat(),
        ax_position=(0, 0),
    )

    ax_record = AxesRecord(
        position=(0, 0),
        calls=[imshow_call],
        decorations=[axis_off_call],
    )

    height, width = img_array.shape[:2]
    dpi = 100
    figsize = (width / dpi, height / dpi)

    record = FigureRecord(
        figsize=figsize,
        dpi=dpi,
        matplotlib_version=matplotlib.__version__,
    )
    record.axes["ax_0_0"] = ax_record

    return record


def compose(
    sources: Dict[Any, Any],
    layout: Optional[Tuple[int, int]] = None,
    canvas_size_mm: Optional[Tuple[float, float]] = None,
    gap_mm: float = 5.0,
    dpi: int = DEFAULT_DPI,
    panel_labels: bool = False,
    label_style: str = "uppercase",
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray, List[RecordingAxes]]]:
    """Compose a new figure from multiple sources (recipes or raw images).

    Supports two modes automatically detected from sources format:

    1. Grid-based: sources={(row, col): path}
       Uses layout=(nrows, ncols) for subplot grid.

    2. Mm-based: sources={path: {"xy_mm": (x, y), "size_mm": (w, h)}}
       Uses canvas_size_mm for precise positioning.

    Parameters
    ----------
    sources : dict
        Either:
        - Grid-based: {(row, col): source_path} mapping positions to sources
        - Mm-based: {source_path: {"xy_mm": (x, y), "size_mm": (w, h)}}
    layout : tuple, optional
        (nrows, ncols) for grid-based composition. Auto-detected if not provided.
    canvas_size_mm : tuple, optional
        (width_mm, height_mm) for mm-based composition. Required for mm-based mode.
    gap_mm : float
        Gap between panels in mm (for auto-layout modes like 'horizontal').
    dpi : int
        DPI for the output figure.
    panel_labels : bool
        If True, add panel labels (A, B, C...) to each panel.
    label_style : str
        'uppercase', 'lowercase', or 'numeric'.
    **kwargs
        Additional arguments passed to figure creation.

    Returns
    -------
    fig : RecordingFigure
        Composed figure (editable, recordable).
    axes : RecordingAxes, ndarray, or list
        Axes of the composed figure.

    Examples
    --------
    Grid-based composition:

    >>> fig, axes = fr.compose(
    ...     layout=(1, 2),
    ...     sources={
    ...         (0, 0): "panel_a.yaml",
    ...         (0, 1): "panel_b.yaml",
    ...     }
    ... )

    Mm-based free-form composition:

    >>> fig, axes = fr.compose(
    ...     canvas_size_mm=(180, 120),
    ...     sources={
    ...         "panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (85, 55)},
    ...         "panel_b.yaml": {"xy_mm": (90, 0), "size_mm": (85, 55)},
    ...         "panel_c.yaml": {"xy_mm": (0, 60), "size_mm": (175, 55)},
    ...     }
    ... )
    """
    if _is_mm_based_sources(sources):
        return _compose_mm_based(
            sources, canvas_size_mm, dpi, panel_labels, label_style, **kwargs
        )
    else:
        return _compose_grid_based(sources, layout, panel_labels, label_style, **kwargs)


def _compose_grid_based(
    sources: Dict[Tuple[int, int], Any],
    layout: Optional[Tuple[int, int]],
    panel_labels: bool,
    label_style: str,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray]]:
    """Grid-based composition using subplots."""
    from .. import subplots

    # Auto-detect layout from source positions
    if layout is None:
        if not sources:
            raise ValueError("sources cannot be empty")
        max_row = max(pos[0] for pos in sources.keys()) + 1
        max_col = max(pos[1] for pos in sources.keys()) + 1
        layout = (max_row, max_col)

    nrows, ncols = layout
    fig, axes = subplots(nrows=nrows, ncols=ncols, **kwargs)

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

        if source_path is not None:
            data_dir = source_path.parent / f"{source_path.stem}_data"
            if data_dir.exists():
                target_ax_key = f"ax_{row}_{col}"
                source_data_dirs[target_ax_key] = data_dir

    if source_data_dirs:
        fig.record.source_data_dirs = source_data_dirs

    # Add panel labels if requested
    if panel_labels:
        _add_panel_labels_grid(axes, nrows, ncols, label_style)

    return fig, axes


def _compose_mm_based(
    sources: Dict[str, Dict[str, Any]],
    canvas_size_mm: Optional[Tuple[float, float]],
    dpi: int,
    panel_labels: bool,
    label_style: str,
    **kwargs,
) -> Tuple[RecordingFigure, List[RecordingAxes]]:
    """Mm-based composition using fig.add_axes() for precise positioning."""
    import matplotlib

    from .._recorder import Recorder
    from .._wrappers import RecordingAxes as RA
    from .._wrappers import RecordingFigure as RF

    if canvas_size_mm is None:
        # Auto-calculate canvas size from panel positions
        max_x = 0
        max_y = 0
        for spec in sources.values():
            xy = spec["xy_mm"]
            size = spec["size_mm"]
            max_x = max(max_x, xy[0] + size[0])
            max_y = max(max_y, xy[1] + size[1])
        canvas_size_mm = (max_x + 5, max_y + 5)  # Add margin

    # Convert canvas size to inches
    width_inch = _mm_to_inch(canvas_size_mm[0])
    height_inch = _mm_to_inch(canvas_size_mm[1])

    # Create figure with specified size
    mpl_fig = matplotlib.pyplot.figure(figsize=(width_inch, height_inch), dpi=dpi)

    # Create recorder for tracking
    recorder = Recorder()
    recorder.start_figure(figsize=(width_inch, height_inch), dpi=dpi)

    # Store mm composition metadata
    recorder.figure_record.composition_mode = "mm"
    recorder.figure_record.canvas_size_mm = canvas_size_mm

    axes_list = []
    source_data_dirs = {}

    for idx, (source_path, spec) in enumerate(sources.items()):
        xy_mm = spec["xy_mm"]
        size_mm = spec["size_mm"]

        # Convert mm to figure fraction (0-1)
        # Note: matplotlib uses bottom-left origin, our mm uses top-left
        left = xy_mm[0] / canvas_size_mm[0]
        # Flip y: top-left origin -> bottom-left origin
        bottom = 1.0 - (xy_mm[1] + size_mm[1]) / canvas_size_mm[1]
        width = size_mm[0] / canvas_size_mm[0]
        height = size_mm[1] / canvas_size_mm[1]

        # Create axes at precise position
        mpl_ax = mpl_fig.add_axes([left, bottom, width, height])

        # Load and replay source
        source_record, ax_key, path = _parse_source_spec_with_path(source_path)
        ax_record = source_record.axes.get(ax_key)

        if ax_record is None:
            available = list(source_record.axes.keys())
            raise ValueError(
                f"Axes '{ax_key}' not found in source. Available: {available}"
            )

        # Wrap as RecordingAxes
        target_ax = RA(mpl_ax, recorder, position=(0, idx))
        axes_list.append(target_ax)

        # Replay the source onto this axes
        _replay_axes_record_mm(mpl_ax, ax_record, recorder.figure_record, idx, spec)

        # Track source data directory
        if path is not None:
            data_dir = path.parent / f"{path.stem}_data"
            if data_dir.exists():
                source_data_dirs[f"ax_mm_{idx}"] = data_dir

    # Wrap as RecordingFigure
    fig = RF(mpl_fig, recorder, axes_list)

    if source_data_dirs:
        fig.record.source_data_dirs = source_data_dirs

    # Add panel labels if requested
    if panel_labels:
        _add_panel_labels_mm(mpl_fig, sources, canvas_size_mm, label_style)

    return fig, axes_list


def _replay_axes_record_mm(
    mpl_ax,
    ax_record,
    fig_record: FigureRecord,
    idx: int,
    spec: Dict[str, Any],
) -> None:
    """Replay axes record for mm-based composition."""
    from .._reproducer._core import _replay_call

    result_cache: Dict[str, Any] = {}

    for call in ax_record.calls:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    for call in ax_record.decorations:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    # Store with mm position info
    ax_key = f"ax_mm_{idx}"
    ax_record_copy = ax_record
    ax_record_copy.mm_position = spec
    fig_record.axes[ax_key] = ax_record_copy


def _add_panel_labels_grid(axes, nrows: int, ncols: int, style: str) -> None:
    """Add panel labels to grid-based composition."""
    labels = _get_panel_labels(nrows * ncols, style)
    idx = 0
    for row in range(nrows):
        for col in range(ncols):
            ax = _get_axes_at(axes, row, col, nrows, ncols)
            mpl_ax = ax._ax if hasattr(ax, "_ax") else ax
            mpl_ax.text(
                -0.1,
                1.1,
                labels[idx],
                transform=mpl_ax.transAxes,
                fontsize=10,
                fontweight="bold",
                va="top",
                ha="right",
            )
            idx += 1


def _add_panel_labels_mm(fig, sources: Dict, canvas_size_mm: Tuple, style: str) -> None:
    """Add panel labels to mm-based composition."""
    labels = _get_panel_labels(len(sources), style)
    for idx, (_, spec) in enumerate(sources.items()):
        xy_mm = spec["xy_mm"]
        # Position label at top-left of panel
        x_frac = xy_mm[0] / canvas_size_mm[0]
        y_frac = 1.0 - xy_mm[1] / canvas_size_mm[1]
        fig.text(
            x_frac - 0.02,
            y_frac + 0.02,
            labels[idx],
            fontsize=10,
            fontweight="bold",
            va="bottom",
            ha="right",
        )


def _get_panel_labels(n: int, style: str) -> List[str]:
    """Generate panel labels based on style."""
    if style == "uppercase":
        return [chr(ord("A") + i) for i in range(n)]
    elif style == "lowercase":
        return [chr(ord("a") + i) for i in range(n)]
    else:  # numeric
        return [str(i + 1) for i in range(n)]


def _parse_source_spec(
    spec: Union[str, Path, FigureRecord, Tuple],
) -> Tuple[FigureRecord, str]:
    """Parse source specification into (FigureRecord, ax_key)."""
    record, ax_key, _ = _parse_source_spec_with_path(spec)
    return record, ax_key


def _parse_source_spec_with_path(
    spec: Union[str, Path, FigureRecord, Tuple],
) -> Tuple[FigureRecord, str, Optional[Path]]:
    """Parse source specification into (FigureRecord, ax_key, source_path)."""
    if isinstance(spec, (str, Path)):
        path = Path(spec)
        if _is_image_file(path):
            return _create_image_record(path), "ax_0_0", path
        return load_recipe(path), "ax_0_0", path
    elif isinstance(spec, FigureRecord):
        return spec, "ax_0_0", None
    elif isinstance(spec, tuple) and len(spec) == 2:
        source, ax_key = spec
        if isinstance(source, (str, Path)):
            path = Path(source)
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
    """Get axes at position, handling different array shapes."""
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
    """Replay all calls from ax_record onto target axes."""
    from .._reproducer._core import _replay_call

    mpl_ax = target_ax._ax if hasattr(target_ax, "_ax") else target_ax
    result_cache: Dict[str, Any] = {}

    for call in ax_record.calls:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    for call in ax_record.decorations:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    ax_key = f"ax_{row}_{col}"
    fig_record.axes[ax_key] = ax_record


__all__ = ["compose"]

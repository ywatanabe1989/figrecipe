#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduce figures from recipe files."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ._recorder import CallRecord, FigureRecord
from ._serializer import load_recipe


def reproduce(
    path: Union[str, Path],
    calls: Optional[List[str]] = None,
    skip_decorations: bool = False,
    apply_overrides: bool = True,
):
    """Reproduce a figure from a recipe file.

    Parameters
    ----------
    path : str or Path
        Path to .yaml or .png recipe file. If .png is provided,
        the corresponding .yaml file will be loaded.
    calls : list of str, optional
        If provided, only reproduce these specific call IDs.
    skip_decorations : bool
        If True, skip decoration calls (labels, legends, etc.).
    apply_overrides : bool
        If True (default), apply .overrides.json if it exists.
        This preserves manual GUI editor changes.

    Returns
    -------
    fig : RecordingFigure
        Reproduced figure (same type as subplots() returns).
    axes : RecordingAxes or ndarray of RecordingAxes
        Reproduced axes (single if 1x1, otherwise numpy array).

    Examples
    --------
    >>> import figrecipe as ps
    >>> fig, ax = ps.reproduce("experiment_001.yaml")
    >>> fig, ax = ps.reproduce("experiment_001.png")  # Also works
    >>> plt.show()
    """
    path = Path(path)

    # Accept both .png and .yaml - find the yaml file
    if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".pdf", ".svg"):
        yaml_path = path.with_suffix(".yaml")
        if not yaml_path.exists():
            raise FileNotFoundError(
                f"Recipe file not found: {yaml_path}. "
                f"Expected .yaml file alongside {path}"
            )
        path = yaml_path

    record = load_recipe(path)

    # Check for override file and merge if exists
    if apply_overrides:
        overrides_path = path.with_suffix(".overrides.json")
        if overrides_path.exists():
            import json

            with open(overrides_path) as f:
                data = json.load(f)

            # Apply style overrides
            manual_overrides = data.get("manual_overrides", {})
            if manual_overrides:
                # Merge overrides into record style
                if record.style is None:
                    record.style = {}
                record.style.update(manual_overrides)

            # Apply call overrides (kwargs changes from editor)
            call_overrides = data.get("call_overrides", {})
            if call_overrides:
                for ax_key, ax_record in record.axes.items():
                    for call in ax_record.calls:
                        if call.id in call_overrides:
                            # Merge call kwargs overrides
                            call.kwargs.update(call_overrides[call.id])

    return reproduce_from_record(
        record,
        calls=calls,
        skip_decorations=skip_decorations,
    )


def reproduce_from_record(
    record: FigureRecord,
    calls: Optional[List[str]] = None,
    skip_decorations: bool = False,
):
    """Reproduce a figure from a FigureRecord.

    Parameters
    ----------
    record : FigureRecord
        The figure record to reproduce.
    calls : list of str, optional
        If provided, only reproduce these specific call IDs.
    skip_decorations : bool
        If True, skip decoration calls.

    Returns
    -------
    fig : RecordingFigure
        Reproduced figure (wrapped).
    axes : RecordingAxes or ndarray of RecordingAxes
        Reproduced axes (wrapped, numpy array for multi-axes).
    """
    from ._recorder import Recorder
    from ._wrappers import RecordingAxes, RecordingFigure

    # Determine grid size from axes positions
    max_row = 0
    max_col = 0
    for ax_key in record.axes.keys():
        parts = ax_key.split("_")
        if len(parts) >= 3:
            max_row = max(max_row, int(parts[1]))
            max_col = max(max_col, int(parts[2]))

    nrows = max_row + 1
    ncols = max_col + 1

    # Create figure
    fig, mpl_axes = plt.subplots(
        nrows,
        ncols,
        figsize=record.figsize,
        dpi=record.dpi,
        constrained_layout=record.constrained_layout,
    )

    # Apply layout if recorded (skip if constrained_layout is used)
    if record.layout is not None and not record.constrained_layout:
        fig.subplots_adjust(**record.layout)

    # Ensure axes is 2D array
    if nrows == 1 and ncols == 1:
        axes_2d = np.array([[mpl_axes]])
    else:
        axes_2d = np.atleast_2d(mpl_axes)
        if nrows == 1:
            axes_2d = axes_2d.reshape(1, -1)
        elif ncols == 1:
            axes_2d = axes_2d.reshape(-1, 1)

    # Apply style BEFORE replaying calls (to match original order:
    # style is applied during subplots(), then user creates plots/decorations)
    if record.style is not None:
        from .styles import apply_style_mm

        for row in range(nrows):
            for col in range(ncols):
                apply_style_mm(axes_2d[row, col], record.style)

    # Result cache for resolving references (e.g., clabel needs ContourSet from contour)
    result_cache: Dict[str, Any] = {}

    # Replay calls on each axes
    for ax_key, ax_record in record.axes.items():
        parts = ax_key.split("_")
        if len(parts) >= 3:
            row, col = int(parts[1]), int(parts[2])
        else:
            row, col = 0, 0

        ax = axes_2d[row, col]

        # Replay plotting calls
        for call in ax_record.calls:
            if calls is not None and call.id not in calls:
                continue
            result = _replay_call(ax, call, result_cache)
            if result is not None:
                result_cache[call.id] = result

        # Replay decorations
        if not skip_decorations:
            for call in ax_record.decorations:
                if calls is not None and call.id not in calls:
                    continue
                result = _replay_call(ax, call, result_cache)
                if result is not None:
                    result_cache[call.id] = result

    # Finalize tick configuration (avoids categorical axis interference)
    from .styles._style_applier import finalize_ticks

    for row in range(nrows):
        for col in range(ncols):
            finalize_ticks(axes_2d[row, col])

    # Apply figure-level labels if recorded
    if record.suptitle is not None:
        text = record.suptitle.get("text", "")
        kwargs = record.suptitle.get("kwargs", {}).copy()
        # Only add y=1.02 if not using constrained_layout (which handles positioning)
        if "y" not in kwargs and not record.constrained_layout:
            kwargs["y"] = 1.02
        fig.suptitle(text, **kwargs)

    if record.supxlabel is not None:
        text = record.supxlabel.get("text", "")
        kwargs = record.supxlabel.get("kwargs", {})
        fig.supxlabel(text, **kwargs)

    if record.supylabel is not None:
        text = record.supylabel.get("text", "")
        kwargs = record.supylabel.get("kwargs", {})
        fig.supylabel(text, **kwargs)

    # Wrap in Recording types (same as subplots() returns)
    recorder = Recorder()
    recorder._figure_record = record

    # Wrap axes in RecordingAxes
    wrapped_axes = np.empty((nrows, ncols), dtype=object)
    for i in range(nrows):
        for j in range(ncols):
            wrapped_axes[i, j] = RecordingAxes(axes_2d[i, j], recorder, position=(i, j))

    # Create RecordingFigure
    wrapped_fig = RecordingFigure(fig, recorder, wrapped_axes.tolist())

    # Return in appropriate format (matching subplots() behavior)
    if nrows == 1 and ncols == 1:
        return wrapped_fig, wrapped_axes[0, 0]
    elif nrows == 1:
        return wrapped_fig, np.array(wrapped_axes[0], dtype=object)
    elif ncols == 1:
        return wrapped_fig, np.array(wrapped_axes[:, 0], dtype=object)
    else:
        return wrapped_fig, wrapped_axes


def _replay_call(
    ax: Axes, call: CallRecord, result_cache: Optional[Dict[str, Any]] = None
) -> Any:
    """Replay a single call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The call to replay.
    result_cache : dict, optional
        Cache mapping call_id -> result for resolving references.

    Returns
    -------
    Any
        Result of the matplotlib call.
    """
    if result_cache is None:
        result_cache = {}

    method_name = call.function

    # Check if it's a seaborn call
    if method_name.startswith("sns."):
        return _replay_seaborn_call(ax, call)

    # Handle violinplot with inner option specially
    if method_name == "violinplot":
        return _replay_violinplot_call(ax, call)

    # Handle joyplot specially (custom method)
    if method_name == "joyplot":
        return _replay_joyplot_call(ax, call)

    # Handle swarmplot specially (custom method)
    if method_name == "swarmplot":
        return _replay_swarmplot_call(ax, call)

    method = getattr(ax, method_name, None)

    if method is None:
        # Method not found, skip
        return None

    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data, result_cache)
        args.append(value)

    # Get kwargs and reconstruct arrays
    kwargs = _reconstruct_kwargs(call.kwargs)

    # Handle special transform markers
    if "transform" in kwargs:
        transform_val = kwargs["transform"]
        if transform_val == "axes":
            kwargs["transform"] = ax.transAxes
        elif transform_val == "data":
            kwargs["transform"] = ax.transData
        elif transform_val == "figure":
            kwargs["transform"] = ax.figure.transFigure
        # If it's already a Transform object or something else, leave it

    # Call the method
    try:
        return method(*args, **kwargs)
    except Exception as e:
        # Log warning but continue
        import warnings

        warnings.warn(f"Failed to replay {method_name}: {e}")
        return None


def _reconstruct_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Reconstruct kwargs, converting 2D lists back to numpy arrays.

    Parameters
    ----------
    kwargs : dict
        Raw kwargs from call record.

    Returns
    -------
    dict
        Kwargs with arrays properly reconstructed.
    """
    result = {}
    for key, value in kwargs.items():
        if isinstance(value, list) and len(value) > 0:
            # Check if it's a 2D list (list of lists) - should be numpy array
            if isinstance(value[0], list):
                result[key] = np.array(value)
            else:
                # 1D list - could be array or just list, try to preserve
                result[key] = value
        else:
            result[key] = value
    return result


def _replay_violinplot_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a violinplot call with inner option support.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The violinplot call to replay.

    Returns
    -------
    Any
        Result of the violinplot call.
    """
    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        args.append(value)

    # Get kwargs and reconstruct arrays
    kwargs = _reconstruct_kwargs(call.kwargs)

    # Extract inner option (not a matplotlib kwarg)
    inner = kwargs.pop("inner", "box")

    # Get display options
    showmeans = kwargs.pop("showmeans", False)
    showmedians = kwargs.pop("showmedians", True)
    showextrema = kwargs.pop("showextrema", False)

    # When using inner box/swarm, suppress default median/extrema lines
    if inner in ("box", "swarm"):
        showmedians = False
        showextrema = False

    # Call matplotlib's violinplot
    try:
        result = ax.violinplot(
            *args,
            showmeans=showmeans,
            showmedians=showmedians,
            showextrema=showextrema,
            **kwargs,
        )

        # Get style settings for inner display
        from .styles import get_style

        style = get_style()
        violin_style = style.get("violinplot", {}) if style else {}

        # Apply alpha from style to violin bodies
        alpha = violin_style.get("alpha", 0.7)
        if "bodies" in result:
            for body in result["bodies"]:
                body.set_alpha(alpha)

        # Determine positions
        dataset = args[0] if args else []
        positions = kwargs.get("positions")
        if positions is None:
            positions = list(range(1, len(dataset) + 1))

        # Overlay inner elements based on inner type
        if inner == "box":
            _add_violin_inner_box(ax, dataset, positions, violin_style)
        elif inner == "swarm":
            _add_violin_inner_swarm(ax, dataset, positions, violin_style)
        elif inner == "stick":
            _add_violin_inner_stick(ax, dataset, positions, violin_style)
        elif inner == "point":
            _add_violin_inner_point(ax, dataset, positions, violin_style)

        return result
    except Exception as e:
        import warnings

        warnings.warn(f"Failed to replay violinplot: {e}")
        return None


def _add_violin_inner_box(ax: Axes, dataset, positions, style: Dict[str, Any]) -> None:
    """Add box plot inside violin for reproduction."""
    from .styles._style_applier import mm_to_pt

    whisker_lw = mm_to_pt(style.get("whisker_mm", 0.2))
    median_size = mm_to_pt(style.get("median_mm", 0.8))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        q1, median, q3 = np.percentile(data, [25, 50, 75])
        iqr = q3 - q1
        whisker_low = max(data.min(), q1 - 1.5 * iqr)
        whisker_high = min(data.max(), q3 + 1.5 * iqr)

        # Draw box (Q1 to Q3)
        ax.vlines(pos, q1, q3, colors="black", linewidths=whisker_lw, zorder=3)
        # Draw whiskers
        ax.vlines(
            pos, whisker_low, q1, colors="black", linewidths=whisker_lw * 0.5, zorder=3
        )
        ax.vlines(
            pos, q3, whisker_high, colors="black", linewidths=whisker_lw * 0.5, zorder=3
        )
        # Draw median as a white dot with black edge
        ax.scatter(
            [pos],
            [median],
            s=median_size**2,
            c="white",
            edgecolors="black",
            linewidths=whisker_lw,
            zorder=4,
        )


def _add_violin_inner_swarm(
    ax: Axes, dataset, positions, style: Dict[str, Any]
) -> None:
    """Add swarm points inside violin for reproduction."""
    from .styles._style_applier import mm_to_pt

    point_size = mm_to_pt(style.get("median_mm", 0.8))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        n = len(data)
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, n)
        x_positions = pos + jitter
        ax.scatter(x_positions, data, s=point_size**2, c="black", alpha=0.5, zorder=3)


def _add_violin_inner_stick(
    ax: Axes, dataset, positions, style: Dict[str, Any]
) -> None:
    """Add stick markers inside violin for reproduction."""
    from .styles._style_applier import mm_to_pt

    lw = mm_to_pt(style.get("whisker_mm", 0.2))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        for val in data:
            ax.hlines(
                val,
                pos - 0.05,
                pos + 0.05,
                colors="black",
                linewidths=lw * 0.5,
                alpha=0.3,
                zorder=3,
            )


def _add_violin_inner_point(
    ax: Axes, dataset, positions, style: Dict[str, Any]
) -> None:
    """Add point markers inside violin for reproduction."""
    from .styles._style_applier import mm_to_pt

    point_size = mm_to_pt(style.get("median_mm", 0.8)) * 0.5

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        x_positions = np.full_like(data, pos)
        ax.scatter(x_positions, data, s=point_size**2, c="black", alpha=0.3, zorder=3)


def _replay_seaborn_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a seaborn call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The seaborn call to replay.

    Returns
    -------
    Any
        Result of the seaborn call.
    """
    try:
        import pandas as pd
        import seaborn as sns
    except ImportError:
        import warnings

        warnings.warn("seaborn/pandas required to replay seaborn calls")
        return None

    # Get the seaborn function name (remove "sns." prefix)
    func_name = call.function[4:]  # Remove "sns."
    func = getattr(sns, func_name, None)

    if func is None:
        import warnings

        warnings.warn(f"Seaborn function {func_name} not found")
        return None

    # Reconstruct data from args
    # Args contain column data with "param" field indicating the parameter name
    data_dict = {}
    param_mapping = {}  # Maps param name to column name

    for arg_data in call.args:
        param = arg_data.get("param")
        name = arg_data.get("name")
        value = _reconstruct_value(arg_data)

        if param is not None:
            # This is a DataFrame column
            col_name = name if name else param
            data_dict[col_name] = value
            param_mapping[param] = col_name

    # Build kwargs
    kwargs = call.kwargs.copy()

    # Remove internal keys
    internal_keys = [k for k in kwargs.keys() if k.startswith("_")]
    for key in internal_keys:
        kwargs.pop(key, None)

    # If we have data columns, create a DataFrame
    if data_dict:
        df = pd.DataFrame(data_dict)
        kwargs["data"] = df

        # Update column name references in kwargs
        for param, col_name in param_mapping.items():
            if param in ["x", "y", "hue", "size", "style", "row", "col"]:
                kwargs[param] = col_name

    # Add the axes
    kwargs["ax"] = ax

    # Convert certain list parameters back to tuples (YAML serializes tuples as lists)
    # 'sizes' in seaborn expects a tuple (min, max) for range, not a list
    if "sizes" in kwargs and isinstance(kwargs["sizes"], list):
        kwargs["sizes"] = tuple(kwargs["sizes"])

    # Call the seaborn function
    try:
        return func(**kwargs)
    except Exception as e:
        import warnings

        warnings.warn(f"Failed to replay sns.{func_name}: {e}")
        return None


def _replay_joyplot_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a joyplot call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The joyplot call to replay.

    Returns
    -------
    Any
        Result of the joyplot call.
    """
    from scipy import stats

    # Reconstruct args
    arrays = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        if isinstance(value, list):
            # Could be a list of arrays
            arrays = [np.asarray(arr) for arr in value]
        else:
            arrays.append(np.asarray(value))

    if not arrays:
        return None

    # Get kwargs
    kwargs = _reconstruct_kwargs(call.kwargs)
    overlap = kwargs.get("overlap", 0.5)
    fill_alpha = kwargs.get("fill_alpha", 0.7)
    line_alpha = kwargs.get("line_alpha", 1.0)
    labels = kwargs.get("labels")

    n_ridges = len(arrays)

    # Get colors from style
    from .styles import get_style

    style = get_style()
    if style and "colors" in style and "palette" in style.colors:
        palette = list(style.colors.palette)
        colors = []
        for c in palette:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                if all(v <= 1.0 for v in c):
                    colors.append(tuple(c))
                else:
                    colors.append(tuple(v / 255.0 for v in c))
            else:
                colors.append(c)
    else:
        colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    # Calculate global x range
    all_data = np.concatenate([np.asarray(arr) for arr in arrays])
    x_min, x_max = np.min(all_data), np.max(all_data)
    x_range = x_max - x_min
    x_padding = x_range * 0.1
    x = np.linspace(x_min - x_padding, x_max + x_padding, 200)

    # Calculate KDEs and find max density for scaling
    kdes = []
    max_density = 0
    for arr in arrays:
        arr = np.asarray(arr)
        if len(arr) > 1:
            kde = stats.gaussian_kde(arr)
            density = kde(x)
            kdes.append(density)
            max_density = max(max_density, np.max(density))
        else:
            kdes.append(np.zeros_like(x))

    # Scale factor for ridge height
    ridge_height = 1.0 / (1.0 - overlap * 0.5) if overlap < 1 else 2.0

    # Get line width from style
    from ._utils._units import mm_to_pt

    lw = mm_to_pt(0.2)  # Default
    if style and "lines" in style:
        lw = mm_to_pt(style.lines.get("trace_mm", 0.2))

    # Plot each ridge from back to front
    for i in range(n_ridges - 1, -1, -1):
        color = colors[i % len(colors)]
        baseline = i * (1.0 - overlap)

        # Scale density to fit nicely
        scaled_density = (
            kdes[i] / max_density * ridge_height if max_density > 0 else kdes[i]
        )

        # Fill
        ax.fill_between(
            x,
            baseline,
            baseline + scaled_density,
            facecolor=color,
            edgecolor="none",
            alpha=fill_alpha,
        )
        # Line on top
        ax.plot(
            x, baseline + scaled_density, color=color, alpha=line_alpha, linewidth=lw
        )

    # Set y limits
    ax.set_ylim(-0.1, n_ridges * (1.0 - overlap) + ridge_height)

    # Set y-axis labels if provided
    if labels:
        y_positions = [(i * (1.0 - overlap)) + 0.3 for i in range(n_ridges)]
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels)
    else:
        ax.set_yticks([])

    return ax


def _replay_swarmplot_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a swarmplot call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The swarmplot call to replay.

    Returns
    -------
    list
        List of PathCollection objects.
    """
    # Reconstruct args
    data = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        if isinstance(value, list):
            # Could be a list of arrays
            data = [np.asarray(arr) for arr in value]
        else:
            data.append(np.asarray(value))

    if not data:
        return []

    # Get kwargs
    kwargs = _reconstruct_kwargs(call.kwargs)
    positions = kwargs.get("positions")
    size = kwargs.get("size", 0.8)
    alpha = kwargs.get("alpha", 0.7)
    jitter = kwargs.get("jitter", 0.3)

    if positions is None:
        positions = list(range(1, len(data) + 1))

    # Get style
    from ._utils._units import mm_to_pt
    from .styles import get_style

    style = get_style()
    size_pt = mm_to_pt(size) ** 2  # matplotlib uses area

    # Get colors
    if style and "colors" in style and "palette" in style.colors:
        palette = list(style.colors.palette)
        colors = []
        for c in palette:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                if all(v <= 1.0 for v in c):
                    colors.append(tuple(c))
                else:
                    colors.append(tuple(v / 255.0 for v in c))
            else:
                colors.append(c)
    else:
        colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    # Random generator for reproducible jitter
    rng = np.random.default_rng(42)

    results = []
    for i, (arr, pos) in enumerate(zip(data, positions)):
        arr = np.asarray(arr)

        # Create jittered x positions using simplified beeswarm
        x_offsets = _beeswarm_positions(arr, jitter, rng)
        x_positions = pos + x_offsets

        c = colors[i % len(colors)]
        result = ax.scatter(
            x_positions,
            arr,
            s=size_pt,
            c=[c],
            alpha=alpha,
        )
        results.append(result)

    return results


def _beeswarm_positions(
    data: np.ndarray,
    width: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Calculate beeswarm-style x positions to minimize overlap.

    Parameters
    ----------
    data : array
        Y values of points.
    width : float
        Maximum jitter width.
    rng : Generator
        Random number generator.

    Returns
    -------
    array
        X offsets for each point.
    """
    n = len(data)
    if n == 0:
        return np.array([])

    # Sort data and get order
    order = np.argsort(data)
    sorted_data = data[order]

    # Group nearby points and offset them
    x_offsets = np.zeros(n)

    # Simple approach: bin by quantiles and spread within each bin
    n_bins = max(1, int(np.sqrt(n)))
    bin_edges = np.percentile(sorted_data, np.linspace(0, 100, n_bins + 1))

    for i in range(n_bins):
        mask = (sorted_data >= bin_edges[i]) & (sorted_data <= bin_edges[i + 1])
        n_in_bin = mask.sum()
        if n_in_bin > 0:
            # Spread points evenly within bin width
            offsets = np.linspace(-width / 2, width / 2, n_in_bin)
            # Add small random noise
            offsets += rng.uniform(-width * 0.1, width * 0.1, n_in_bin)
            x_offsets[mask] = offsets

    # Restore original order
    result = np.zeros(n)
    result[order] = x_offsets
    return result


def _reconstruct_value(
    arg_data: Dict[str, Any], result_cache: Optional[Dict[str, Any]] = None
) -> Any:
    """Reconstruct a value from serialized arg data.

    Parameters
    ----------
    arg_data : dict
        Serialized argument data.
    result_cache : dict, optional
        Cache mapping call_id -> result for resolving references.

    Returns
    -------
    Any
        Reconstructed value.
    """
    if result_cache is None:
        result_cache = {}

    # Check if we have a pre-loaded array
    if "_loaded_array" in arg_data:
        return arg_data["_loaded_array"]

    data = arg_data.get("data")

    # Check if it's a reference to another call's result (e.g., ContourSet for clabel)
    if isinstance(data, dict) and "__ref__" in data:
        ref_id = data["__ref__"]
        if ref_id in result_cache:
            return result_cache[ref_id]
        else:
            import warnings

            warnings.warn(f"Could not resolve reference to {ref_id}")
            return None

    # Check if it's a list of arrays (e.g., boxplot, violinplot)
    if arg_data.get("_is_array_list") and isinstance(data, list):
        dtype = arg_data.get("dtype")
        # Convert each inner list to numpy array
        return [
            np.array(arr_data, dtype=dtype if isinstance(dtype, str) else None)
            for arr_data in data
        ]

    # If data is a list, convert to numpy array
    if isinstance(data, list):
        dtype = arg_data.get("dtype")
        try:
            return np.array(data, dtype=dtype if dtype else None)
        except (TypeError, ValueError):
            return np.array(data)

    return data


def get_recipe_info(path: Union[str, Path]) -> Dict[str, Any]:
    """Get information about a recipe without reproducing.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    dict
        Recipe information including:
        - id: Figure ID
        - created: Creation timestamp
        - matplotlib_version: Version used
        - figsize: Figure size
        - n_axes: Number of axes
        - calls: List of call IDs
    """
    record = load_recipe(path)

    all_calls = []
    for ax_record in record.axes.values():
        for call in ax_record.calls:
            all_calls.append(
                {
                    "id": call.id,
                    "function": call.function,
                    "n_args": len(call.args),
                    "kwargs": list(call.kwargs.keys()),
                }
            )
        for call in ax_record.decorations:
            all_calls.append(
                {
                    "id": call.id,
                    "function": call.function,
                    "type": "decoration",
                }
            )

    return {
        "id": record.id,
        "created": record.created,
        "matplotlib_version": record.matplotlib_version,
        "figsize": record.figsize,
        "dpi": record.dpi,
        "n_axes": len(record.axes),
        "calls": all_calls,
    }

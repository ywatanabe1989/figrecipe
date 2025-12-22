#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduce figures from recipe files."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ._recorder import FigureRecord, CallRecord
from ._serializer import load_recipe


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
        Reproduced axes (single if 1x1, otherwise list).

    Examples
    --------
    >>> import figrecipe as ps
    >>> fig, ax = ps.reproduce("experiment_001.yaml")
    >>> plt.show()
    """
    record = load_recipe(path)
    return reproduce_from_record(
        record,
        calls=calls,
        skip_decorations=skip_decorations,
    )


def reproduce_from_record(
    record: FigureRecord,
    calls: Optional[List[str]] = None,
    skip_decorations: bool = False,
) -> Tuple[Figure, Union[Axes, List[Axes]]]:
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
    fig : matplotlib.figure.Figure
        Reproduced figure.
    axes : Axes or list of Axes
        Reproduced axes.
    """
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

    # Apply layout if recorded
    if record.layout is not None:
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
            _replay_call(ax, call)

        # Replay decorations
        if not skip_decorations:
            for call in ax_record.decorations:
                if calls is not None and call.id not in calls:
                    continue
                _replay_call(ax, call)

    # Return in appropriate format
    if nrows == 1 and ncols == 1:
        return fig, axes_2d[0, 0]
    elif nrows == 1:
        return fig, list(axes_2d[0])
    elif ncols == 1:
        return fig, list(axes_2d[:, 0])
    else:
        return fig, axes_2d.tolist()


def _replay_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a single call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The call to replay.

    Returns
    -------
    Any
        Result of the matplotlib call.
    """
    method_name = call.function

    # Check if it's a seaborn call
    if method_name.startswith("sns."):
        return _replay_seaborn_call(ax, call)

    method = getattr(ax, method_name, None)

    if method is None:
        # Method not found, skip
        return None

    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        args.append(value)

    # Get kwargs
    kwargs = call.kwargs.copy()

    # Call the method
    try:
        return method(*args, **kwargs)
    except Exception as e:
        # Log warning but continue
        import warnings
        warnings.warn(f"Failed to replay {method_name}: {e}")
        return None


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
        import seaborn as sns
        import pandas as pd
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


def _reconstruct_value(arg_data: Dict[str, Any]) -> Any:
    """Reconstruct a value from serialized arg data.

    Parameters
    ----------
    arg_data : dict
        Serialized argument data.

    Returns
    -------
    Any
        Reconstructed value.
    """
    # Check if we have a pre-loaded array
    if "_loaded_array" in arg_data:
        return arg_data["_loaded_array"]

    data = arg_data.get("data")

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
            all_calls.append({
                "id": call.id,
                "function": call.function,
                "n_args": len(call.args),
                "kwargs": list(call.kwargs.keys()),
            })
        for call in ax_record.decorations:
            all_calls.append({
                "id": call.id,
                "function": call.function,
                "type": "decoration",
            })

    return {
        "id": record.id,
        "created": record.created,
        "matplotlib_version": record.matplotlib_version,
        "figsize": record.figsize,
        "dpi": record.dpi,
        "n_axes": len(record.axes),
        "calls": all_calls,
    }

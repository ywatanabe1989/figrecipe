#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seaborn recording support for RecordingAxes."""

from typing import TYPE_CHECKING, Any, Dict, Optional

import numpy as np

if TYPE_CHECKING:
    from .._recorder import Recorder


def record_seaborn_call(
    recorder: "Recorder",
    position: tuple,
    func_name: str,
    args: tuple,
    kwargs: Dict[str, Any],
    data_arrays: Dict[str, np.ndarray],
    call_id: Optional[str] = None,
) -> None:
    """Record a seaborn plotting call.

    Parameters
    ----------
    recorder : Recorder
        The recorder instance.
    position : tuple
        (row, col) position of axes.
    func_name : str
        Name of the seaborn function (e.g., 'scatterplot').
    args : tuple
        Processed positional arguments.
    kwargs : dict
        Processed keyword arguments.
    data_arrays : dict
        Dictionary of array data extracted from DataFrame/arrays.
    call_id : str, optional
        Custom ID for this call.
    """
    from .._recorder import CallRecord

    # Generate call ID if not provided
    if call_id is None:
        call_id = recorder._generate_call_id(f"sns_{func_name}")

    # Process data arrays into args format
    processed_args = _process_seaborn_args(args, data_arrays)

    # Process DataFrame column data
    _add_column_data_to_args(processed_args, data_arrays)

    # Process kwarg arrays
    processed_kwargs = _process_seaborn_kwargs(kwargs, data_arrays)

    # Create call record
    record = CallRecord(
        id=call_id,
        function=f"sns.{func_name}",
        args=processed_args,
        kwargs=processed_kwargs,
        ax_position=position,
    )

    # Add to axes record
    ax_record = recorder.figure_record.get_or_create_axes(*position)
    ax_record.add_call(record)


def _process_seaborn_args(args: tuple, data_arrays: Dict[str, np.ndarray]) -> list:
    """Process seaborn positional arguments."""
    from .._utils._numpy_io import should_store_inline, to_serializable

    processed_args = []
    for i, arg in enumerate(args):
        if arg == "__ARRAY__":
            key = f"_arg_{i}"
            if key in data_arrays:
                arr = data_arrays[key]
                if should_store_inline(arr):
                    processed_args.append(
                        {
                            "name": f"arg{i}",
                            "data": to_serializable(arr),
                            "dtype": str(arr.dtype),
                        }
                    )
                else:
                    processed_args.append(
                        {
                            "name": f"arg{i}",
                            "data": "__FILE__",
                            "dtype": str(arr.dtype),
                            "_array": arr,
                        }
                    )
        else:
            processed_args.append({"name": f"arg{i}", "data": arg})

    return processed_args


def _add_column_data_to_args(
    processed_args: list, data_arrays: Dict[str, np.ndarray]
) -> None:
    """Add DataFrame column data to processed args."""
    from .._utils._numpy_io import should_store_inline, to_serializable

    for key, arr in data_arrays.items():
        if key.startswith("_col_"):
            param_name = key[5:]  # Remove "_col_" prefix
            col_name = data_arrays.get(f"_colname_{param_name}", param_name)
            if should_store_inline(arr):
                processed_args.append(
                    {
                        "name": col_name,
                        "param": param_name,
                        "data": to_serializable(arr),
                        "dtype": str(arr.dtype),
                    }
                )
            else:
                processed_args.append(
                    {
                        "name": col_name,
                        "param": param_name,
                        "data": "__FILE__",
                        "dtype": str(arr.dtype),
                        "_array": arr,
                    }
                )


def _process_seaborn_kwargs(
    kwargs: Dict[str, Any], data_arrays: Dict[str, np.ndarray]
) -> Dict[str, Any]:
    """Process seaborn keyword arguments."""
    from .._utils._numpy_io import should_store_inline, to_serializable

    processed_kwargs = dict(kwargs)
    for key, value in kwargs.items():
        if value == "__ARRAY__":
            arr_key = f"_kwarg_{key}"
            if arr_key in data_arrays:
                arr = data_arrays[arr_key]
                if should_store_inline(arr):
                    processed_kwargs[key] = to_serializable(arr)
                else:
                    processed_kwargs[key] = "__FILE__"
                    processed_kwargs[f"_array_{key}"] = arr

    return processed_kwargs


__all__ = ["record_seaborn_call"]

# EOF

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilities for recorder argument processing."""

from typing import Any, Dict, List

import numpy as np


def process_args(
    args: tuple,
    method_name: str,
    get_arg_names_func,
    is_serializable_func,
) -> List[Dict[str, Any]]:
    """Process positional arguments for storage.

    Parameters
    ----------
    args : tuple
        Raw positional arguments.
    method_name : str
        Name of the method.
    get_arg_names_func : callable
        Function to get argument names.
    is_serializable_func : callable
        Function to check serializability.

    Returns
    -------
    list
        Processed args with name and data.
    """
    from ._utils._numpy_io import should_store_inline, to_serializable

    processed = []
    arg_names = get_arg_names_func(method_name, len(args))

    for name, value in zip(arg_names, args):
        processed_arg = _process_single_arg(
            name, value, should_store_inline, to_serializable, is_serializable_func
        )
        processed.append(processed_arg)

    return processed


def _process_single_arg(
    name: str,
    value: Any,
    should_store_inline,
    to_serializable,
    is_serializable_func,
) -> Dict[str, Any]:
    """Process a single argument value."""
    # Handle result references (e.g., ContourSet for clabel)
    if isinstance(value, dict) and "__ref__" in value:
        return {"name": name, "data": {"__ref__": value["__ref__"]}}

    if isinstance(value, np.ndarray):
        return _process_ndarray(name, value, should_store_inline, to_serializable)

    if hasattr(value, "values"):  # pandas
        arr = np.asarray(value)
        return _process_ndarray(name, arr, should_store_inline, to_serializable)

    if (
        isinstance(value, (list, tuple))
        and len(value) > 0
        and isinstance(value[0], np.ndarray)
    ):
        # List of arrays (e.g., boxplot, violinplot data)
        return _process_array_list(name, value, to_serializable)

    # Scalar or other serializable value
    return _process_scalar(name, value, is_serializable_func)


def _process_ndarray(
    name: str, value: np.ndarray, should_store_inline, to_serializable
) -> Dict[str, Any]:
    """Process numpy array argument."""
    if should_store_inline(value):
        return {
            "name": name,
            "data": to_serializable(value),
            "dtype": str(value.dtype),
        }
    else:
        # Mark for file storage (will be handled by serializer)
        return {
            "name": name,
            "data": "__FILE__",
            "dtype": str(value.dtype),
            "_array": value,  # Temporary, removed during serialization
        }


def _process_array_list(name: str, value: list, to_serializable) -> Dict[str, Any]:
    """Process list of arrays argument."""
    arrays_data = [to_serializable(arr) for arr in value]
    dtypes = [str(arr.dtype) for arr in value]
    return {
        "name": name,
        "data": arrays_data,
        "dtype": (dtypes[0] if len(set(dtypes)) == 1 else dtypes),
        "_is_array_list": True,
    }


def _process_scalar(name: str, value: Any, is_serializable_func) -> Dict[str, Any]:
    """Process scalar or other value."""
    try:
        return {
            "name": name,
            "data": value if is_serializable_func(value) else str(value),
        }
    except (TypeError, ValueError):
        return {"name": name, "data": str(value)}


__all__ = ["process_args"]

# EOF

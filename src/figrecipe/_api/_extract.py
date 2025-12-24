#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data extraction helpers for the public API."""

from typing import Any, Dict, Set

import numpy as np

# Decoration functions to skip when extracting data
DECORATION_FUNCS: Set[str] = {
    "set_xlabel",
    "set_ylabel",
    "set_title",
    "set_xlim",
    "set_ylim",
    "legend",
    "grid",
    "axhline",
    "axvline",
    "text",
    "annotate",
}


def to_array(data: Any) -> np.ndarray:
    """Convert data to numpy array, handling YAML types.

    Parameters
    ----------
    data : any
        Data to convert.

    Returns
    -------
    np.ndarray
        Converted numpy array.
    """
    # Handle dict with 'data' key (serialized array format)
    if isinstance(data, dict) or (hasattr(data, "keys") and "data" in data):
        return np.array(data["data"])
    if hasattr(data, "tolist"):  # Already array-like
        return np.array(data)
    return np.array(
        list(data) if hasattr(data, "__iter__") and not isinstance(data, str) else data
    )


def extract_call_data(call) -> Dict[str, Any]:
    """Extract data arrays from a single call record.

    Parameters
    ----------
    call : CallRecord
        The call to extract data from.

    Returns
    -------
    dict
        Dictionary with extracted data arrays.
    """
    call_data = {}

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
            if (
                isinstance(val, (list, tuple))
                or hasattr(val, "__iter__")
                and not isinstance(val, str)
            ):
                call_data[key] = to_array(val)
            else:
                call_data[key] = val

    return call_data


__all__ = [
    "DECORATION_FUNCS",
    "to_array",
    "extract_call_data",
]

# EOF

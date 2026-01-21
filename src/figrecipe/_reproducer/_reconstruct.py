#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Value reconstruction utilities for recipe reproduction.

These functions handle converting serialized recipe data back into
Python objects (numpy arrays, lists, etc.) that matplotlib can use.
"""

from typing import Any, Dict, Optional

import numpy as np


def reconstruct_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
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
        # Handle 'colors' parameter specially - must be a list for pie/bar/etc.
        # A single color string like 'red' would be interpreted as ['r','e','d']
        if key == "colors" and isinstance(value, str):
            result[key] = [value]
        elif isinstance(value, list) and len(value) > 0:
            # Check if it's a 2D list (list of lists) - should be numpy array
            if isinstance(value[0], list):
                result[key] = np.array(value)
            else:
                # 1D list - could be array or just list, try to preserve
                result[key] = value
        else:
            result[key] = value
    return result


def reconstruct_value(
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
            # Handle inhomogeneous arrays (e.g., boxplot data with different group sizes)
            # Return as list for methods that accept list input
            return data

    return data


# EOF

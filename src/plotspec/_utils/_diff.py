#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilities for comparing default vs passed values."""

from typing import Any, Dict, Optional

import numpy as np


def is_default_value(value: Any, default: Any) -> bool:
    """Check if value equals the default.

    Parameters
    ----------
    value : Any
        Value to check.
    default : Any
        Default value.

    Returns
    -------
    bool
        True if value equals default.
    """
    # Handle None
    if value is None and default is None:
        return True

    # Handle numpy arrays
    if isinstance(value, np.ndarray) or isinstance(default, np.ndarray):
        try:
            return np.array_equal(value, default)
        except (TypeError, ValueError):
            return False

    # Handle callables
    if callable(value) or callable(default):
        return value is default

    # Standard comparison
    try:
        return value == default
    except (TypeError, ValueError):
        return False


def get_non_default_kwargs(
    passed_kwargs: Dict[str, Any],
    signature_defaults: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Filter kwargs to only include non-default values.

    Parameters
    ----------
    passed_kwargs : dict
        Kwargs that were passed to the function.
    signature_defaults : dict, optional
        Default values from function signature.

    Returns
    -------
    dict
        Only kwargs that differ from defaults.
    """
    if signature_defaults is None:
        # If no defaults provided, return all kwargs
        return passed_kwargs.copy()

    non_default = {}
    for key, value in passed_kwargs.items():
        default = signature_defaults.get(key)
        if not is_default_value(value, default):
            non_default[key] = value

    return non_default


def merge_with_defaults(
    stored_kwargs: Dict[str, Any],
    signature_defaults: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge stored kwargs with defaults for reproduction.

    Parameters
    ----------
    stored_kwargs : dict
        Non-default kwargs that were stored.
    signature_defaults : dict
        Default values from function signature.

    Returns
    -------
    dict
        Complete kwargs for function call.
    """
    merged = signature_defaults.copy()
    merged.update(stored_kwargs)
    return merged

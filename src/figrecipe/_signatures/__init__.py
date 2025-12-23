#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Matplotlib function signatures for validation and defaults."""

from ._loader import (
    get_defaults,
    get_signature,
    list_plotting_methods,
    validate_kwargs,
)

__all__ = [
    "get_signature",
    "get_defaults",
    "validate_kwargs",
    "list_plotting_methods",
]

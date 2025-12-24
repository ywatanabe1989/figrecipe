#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DotDict class for nested dictionary access with dot notation."""

from typing import Any


class DotDict(dict):
    """Dictionary with dot-notation access to nested keys.

    Examples
    --------
    >>> d = DotDict({"axes": {"width_mm": 40}})
    >>> d.axes.width_mm
    40
    """

    def __getattr__(self, key: str) -> Any:
        # Handle special methods first
        if key == "to_subplots_kwargs":
            from ._style_loader import to_subplots_kwargs

            return lambda: to_subplots_kwargs(self)
        try:
            value = self[key]
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
                self[key] = value
            return value
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

    def __repr__(self) -> str:
        return f"DotDict({super().__repr__()})"

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default, supporting nested keys with dots."""
        if "." in key:
            parts = key.split(".")
            value = self
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        return super().get(key, default)

    def flatten(self, prefix: str = "") -> dict:
        """Flatten nested dict to single level with underscore-joined keys."""
        result = {}
        for k, v in self.items():
            new_key = f"{prefix}_{k}" if prefix else k
            if isinstance(v, dict):
                result.update(DotDict(v).flatten(new_key))
            else:
                result[new_key] = v
        return result


__all__ = ["DotDict"]

# EOF

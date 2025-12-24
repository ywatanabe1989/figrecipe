#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seaborn proxy for figrecipe.

Provides lazy seaborn integration via ps.sns.
"""

__all__ = [
    "sns",
]

# Lazy import for seaborn to avoid hard dependency
_sns_recorder = None


def _get_sns():
    """Get the seaborn recorder (lazy initialization)."""
    global _sns_recorder
    if _sns_recorder is None:
        from .._seaborn import get_seaborn_recorder

        _sns_recorder = get_seaborn_recorder()
    return _sns_recorder


class _SeabornProxy:
    """Proxy object for seaborn access via ps.sns."""

    def __getattr__(self, name: str):
        return getattr(_get_sns(), name)


# Create seaborn proxy
sns = _SeabornProxy()

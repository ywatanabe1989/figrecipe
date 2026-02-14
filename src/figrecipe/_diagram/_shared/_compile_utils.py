#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared compile utilities."""

import re


def _sanitize_id(s: str) -> str:
    """Make string safe for use as node ID."""
    # Remove or replace problematic characters for Mermaid/Graphviz
    s = re.sub(r"[^\w]", "_", s)  # Replace non-word chars with _
    s = re.sub(r"_+", "_", s)  # Collapse multiple underscores
    s = s.strip("_")  # Remove leading/trailing underscores
    return s or "node"


__all__ = ["_sanitize_id"]

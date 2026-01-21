#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figrecipe MCP server module.

Requires fastmcp>=2.0.0 (Python 3.10+). Install with:
    pip install figrecipe[mcp]
"""

try:
    from .server import mcp

    __all__ = ["mcp"]
except ImportError:
    # fastmcp not installed - MCP functionality unavailable
    mcp = None
    __all__ = []

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel drag snapshot functionality with server-side isolated rendering.

This module provides clean panel snapshots rendered in isolation (no overlap)
by fetching from the server, with async caching for smooth UX.
"""

SCRIPTS_PANEL_DRAG_SNAPSHOT = """
// ===== PANEL DRAG SNAPSHOT (DISABLED - corrupts figure state) =====
// Server-side snapshot rendering was disabled because matplotlib figures
// are not thread-safe. Modifying visibility to render isolated panels
// corrupts the shared figure state in Flask's threaded mode.

// No-op stubs to prevent errors from panel_drag.py calls
function startSnapshotDrag(panelIndex, imgRect, initialPos) {
    // Disabled - no snapshot during drag
}

function updateSnapshotPosition(pos, imgRect) {
    // Disabled - no snapshot during drag
}

function endSnapshotDrag() {
    // Disabled - no snapshot during drag
}

// No initialization needed
"""

__all__ = ["SCRIPTS_PANEL_DRAG_SNAPSHOT"]

# EOF

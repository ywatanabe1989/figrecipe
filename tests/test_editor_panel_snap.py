#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for panel snapping functionality in the figure editor."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestPanelSnapScript:
    """Test that panel snapping JavaScript module is properly defined."""

    def test_panel_snap_script_exists(self):
        """Test that SCRIPTS_PANEL_SNAP is defined and exported."""
        from figrecipe._editor._templates._scripts import SCRIPTS_PANEL_SNAP

        assert SCRIPTS_PANEL_SNAP is not None
        assert len(SCRIPTS_PANEL_SNAP) > 0

    def test_snap_config_defined(self):
        """Test that SNAP_CONFIG is defined with expected properties."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "SNAP_CONFIG" in SCRIPTS_PANEL_SNAP
        assert "gridSize" in SCRIPTS_PANEL_SNAP
        assert "snapThreshold" in SCRIPTS_PANEL_SNAP
        assert "magneticZone" in SCRIPTS_PANEL_SNAP

    def test_apply_snapping_function(self):
        """Test that applySnapping function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function applySnapping(" in SCRIPTS_PANEL_SNAP

    def test_snap_to_grid_function(self):
        """Test that snapToGrid function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function snapToGrid(" in SCRIPTS_PANEL_SNAP

    def test_show_snap_guides_function(self):
        """Test that showSnapGuides function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function showSnapGuides(" in SCRIPTS_PANEL_SNAP

    def test_hide_snap_guides_function(self):
        """Test that hideSnapGuides function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function hideSnapGuides(" in SCRIPTS_PANEL_SNAP

    def test_toggle_snapping_function(self):
        """Test that toggleSnapping function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function toggleSnapping(" in SCRIPTS_PANEL_SNAP

    def test_magnetic_attraction_function(self):
        """Test that applyMagnetic function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function applyMagnetic(" in SCRIPTS_PANEL_SNAP


class TestAltDragFineMovement:
    """Test Alt+Drag for fine movement (disables snapping)."""

    def test_alt_key_disables_snapping_in_drag_move(self):
        """Test that Alt key check is in handlePanelDragMove."""
        from figrecipe._editor._templates._scripts._panel_drag import SCRIPTS_PANEL_DRAG

        # Alt key should disable snapping during drag
        assert "!event.altKey" in SCRIPTS_PANEL_DRAG
        assert "applySnapping" in SCRIPTS_PANEL_DRAG

    def test_alt_key_disables_snapping_in_drag_end(self):
        """Test that Alt key check is in handlePanelDragEnd."""
        from figrecipe._editor._templates._scripts._panel_drag import SCRIPTS_PANEL_DRAG

        # Should have two !event.altKey checks (move and end)
        assert SCRIPTS_PANEL_DRAG.count("!event.altKey") >= 2


class TestPanelSnapUI:
    """Test panel snapping UI documentation."""

    def test_alt_drag_in_shortcuts_modal(self):
        """Test that Alt+Drag is documented in shortcuts modal."""
        from figrecipe._editor._templates._html import HTML_TEMPLATE

        assert "Panel Editing" in HTML_TEMPLATE
        assert "Alt" in HTML_TEMPLATE
        assert "Drag" in HTML_TEMPLATE
        assert "no snapping" in HTML_TEMPLATE

    def test_drag_snapping_documented(self):
        """Test that drag snapping is documented."""
        from figrecipe._editor._templates._html import HTML_TEMPLATE

        assert "snaps to grid" in HTML_TEMPLATE


class TestSnapGuides:
    """Test visual alignment guides."""

    def test_snap_guides_array(self):
        """Test that snapGuides array is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "let snapGuides = []" in SCRIPTS_PANEL_SNAP

    def test_guide_element_creation(self):
        """Test that guide elements are created with correct styling."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "snap-guide" in SCRIPTS_PANEL_SNAP
        assert "position: absolute" in SCRIPTS_PANEL_SNAP

    def test_guide_visibility_control(self):
        """Test that guide visibility is controlled."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert (
            "display: 'none'" in SCRIPTS_PANEL_SNAP
            or "display: none" in SCRIPTS_PANEL_SNAP
        )
        assert (
            "display: 'block'" in SCRIPTS_PANEL_SNAP
            or "display = 'block'" in SCRIPTS_PANEL_SNAP
        )


class TestSnapTargets:
    """Test snap target detection."""

    def test_get_snap_targets_function(self):
        """Test that getSnapTargets function is defined."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "function getSnapTargets(" in SCRIPTS_PANEL_SNAP

    def test_panel_edge_snapping(self):
        """Test that panel edge snapping targets are detected."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "edge-left" in SCRIPTS_PANEL_SNAP
        assert "edge-right" in SCRIPTS_PANEL_SNAP
        assert "edge-top" in SCRIPTS_PANEL_SNAP
        assert "edge-bottom" in SCRIPTS_PANEL_SNAP

    def test_center_snapping(self):
        """Test that center snapping is available."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "centerX" in SCRIPTS_PANEL_SNAP
        assert "centerY" in SCRIPTS_PANEL_SNAP
        assert "type: 'center'" in SCRIPTS_PANEL_SNAP

    def test_figure_edge_snapping(self):
        """Test that figure edge snapping is available."""
        from figrecipe._editor._templates._scripts._panel_snap import SCRIPTS_PANEL_SNAP

        assert "figure-edge" in SCRIPTS_PANEL_SNAP
        assert "figure-center" in SCRIPTS_PANEL_SNAP


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

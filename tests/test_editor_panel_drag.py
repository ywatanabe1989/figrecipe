#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for panel drag functionality."""


class TestPanelDragScript:
    """Test the panel drag JavaScript module."""

    def test_panel_drag_script_exists(self):
        """Test that panel drag script module exists."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert SCRIPTS_PANEL_DRAG
        assert len(SCRIPTS_PANEL_DRAG) > 100

    def test_drag_allowed_types_includes_axes(self):
        """Test that axes type is in drag allowed types."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "dragAllowedTypes" in SCRIPTS_PANEL_DRAG
        assert "'axes'" in SCRIPTS_PANEL_DRAG

    def test_drag_allowed_types_includes_image(self):
        """Test that image type (imshow) is in drag allowed types."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "'image'" in SCRIPTS_PANEL_DRAG

    def test_drag_allowed_types_includes_contour(self):
        """Test that contour type (contour/contourf) is in drag allowed types."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "'contour'" in SCRIPTS_PANEL_DRAG

    def test_drag_allowed_types_includes_quadmesh(self):
        """Test that quadmesh type (pcolormesh/specgram) is in drag allowed types."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "'quadmesh'" in SCRIPTS_PANEL_DRAG

    def test_drag_allowed_types_includes_quiver(self):
        """Test that quiver type is in drag allowed types."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "'quiver'" in SCRIPTS_PANEL_DRAG


class TestPanelDragIntegration:
    """Test panel drag integration with other scripts."""

    def test_panel_drag_in_combined_scripts(self):
        """Test that panel drag script is included in combined scripts."""
        from figrecipe._editor._templates._scripts import SCRIPTS

        assert "initPanelDrag" in SCRIPTS
        assert "handlePanelDragEnd" in SCRIPTS

    def test_panel_positions_variable(self):
        """Test that panelPositions variable is defined."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "panelPositions" in SCRIPTS_PANEL_DRAG


# EOF

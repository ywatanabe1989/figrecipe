#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for panel drag snapshot visual feedback."""


class TestPanelDragSnapshotScript:
    """Test the panel drag snapshot JavaScript."""

    def test_snapshot_script_exists(self):
        """Test that snapshot script module exists."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert SCRIPTS_PANEL_DRAG_SNAPSHOT
        assert len(SCRIPTS_PANEL_DRAG_SNAPSHOT) > 100

    def test_snapshot_in_combined_scripts(self):
        """Test that snapshot script is included in combined scripts."""
        from figrecipe._editor._templates._scripts import SCRIPTS

        assert "panelDragSnapshot" in SCRIPTS
        assert "fetchPanelSnapshot" in SCRIPTS  # Server-side fetch

    def test_fetch_panel_snapshot_function(self):
        """Test fetchPanelSnapshot function is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function fetchPanelSnapshot" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_show_panel_snapshot_function(self):
        """Test showPanelSnapshot function is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function showPanelSnapshot" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_hide_panel_snapshot_function(self):
        """Test hidePanelSnapshot function is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function hidePanelSnapshot" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_start_snapshot_drag_function(self):
        """Test startSnapshotDrag function is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function startSnapshotDrag" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_update_snapshot_position_function(self):
        """Test updateSnapshotPosition function is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function updateSnapshotPosition" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_end_snapshot_drag_function(self):
        """Test endSnapshotDrag function is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function endSnapshotDrag" in SCRIPTS_PANEL_DRAG_SNAPSHOT


class TestPanelDragSnapshotIntegration:
    """Test integration with panel drag module."""

    def test_panel_drag_calls_start_snapshot(self):
        """Test that panel drag calls startSnapshotDrag on drag start."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "startSnapshotDrag" in SCRIPTS_PANEL_DRAG

    def test_panel_drag_calls_update_snapshot(self):
        """Test that panel drag calls updateSnapshotPosition on drag move."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "updateSnapshotPosition" in SCRIPTS_PANEL_DRAG

    def test_panel_drag_calls_end_snapshot(self):
        """Test that panel drag calls endSnapshotDrag on drag end."""
        from figrecipe._editor._templates._scripts._panel_drag import (
            SCRIPTS_PANEL_DRAG,
        )

        assert "endSnapshotDrag" in SCRIPTS_PANEL_DRAG


class TestSnapshotStyling:
    """Test snapshot visual styling."""

    def test_snapshot_has_opacity(self):
        """Test that snapshot has transparency applied."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "opacity: 0.7" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_snapshot_has_shadow(self):
        """Test that snapshot has drop shadow for depth."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "box-shadow" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_snapshot_uses_server_fetch(self):
        """Test that snapshot uses server-side rendering."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "/get_panel_snapshot/" in SCRIPTS_PANEL_DRAG_SNAPSHOT
        assert "fetch(" in SCRIPTS_PANEL_DRAG_SNAPSHOT


# EOF

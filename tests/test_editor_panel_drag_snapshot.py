#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for panel drag snapshot functionality (currently disabled)."""


class TestPanelDragSnapshotScript:
    """Test the panel drag snapshot JavaScript (disabled - no-op stubs)."""

    def test_snapshot_script_exists(self):
        """Test that snapshot script module exists."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert SCRIPTS_PANEL_DRAG_SNAPSHOT
        assert len(SCRIPTS_PANEL_DRAG_SNAPSHOT) > 50

    def test_snapshot_is_disabled(self):
        """Test that snapshot feature is marked as disabled."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "DISABLED" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_start_snapshot_drag_stub(self):
        """Test startSnapshotDrag no-op stub is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function startSnapshotDrag" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_update_snapshot_position_stub(self):
        """Test updateSnapshotPosition no-op stub is defined."""
        from figrecipe._editor._templates._scripts._panel_drag_snapshot import (
            SCRIPTS_PANEL_DRAG_SNAPSHOT,
        )

        assert "function updateSnapshotPosition" in SCRIPTS_PANEL_DRAG_SNAPSHOT

    def test_end_snapshot_drag_stub(self):
        """Test endSnapshotDrag no-op stub is defined."""
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


# EOF

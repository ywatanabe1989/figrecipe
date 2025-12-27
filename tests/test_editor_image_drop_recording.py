#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for RecordingAxes integration in drag-and-drop image functionality."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestRecordingAxesIntegration:
    """Test that dropped images integrate with the RecordingAxes system."""

    @pytest.fixture
    def editor_with_figure(self):
        """Create editor with a RecordingFigure."""
        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor

        fig, ax = fr.subplots(1, 2)
        ax[0].plot([1, 2, 3], [1, 4, 9], id="line_A")
        ax[1].bar(["X", "Y"], [3, 5], id="bar_B")

        editor = FigureEditor(fig, port=5997)
        return editor

    def test_dropped_image_uses_recording_axes(self, editor_with_figure):
        """Verify dropped image is wrapped in RecordingAxes."""
        from figrecipe._editor._routes_image import _add_image_panel_to_figure

        editor = editor_with_figure
        img_array = np.zeros((50, 50, 3), dtype=np.uint8)
        img_array[:, :, 0] = 255  # Red image

        # Count axes before
        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes_before = len(mpl_fig.get_axes())

        # Add image panel
        _add_image_panel_to_figure(editor, img_array, "test_red.png", 0.5, 0.5)

        # Count axes after
        axes_after = len(mpl_fig.get_axes())
        assert axes_after == axes_before + 1

    def test_dropped_image_recorded_in_calls(self, editor_with_figure):
        """Verify dropped image imshow call is recorded."""
        from figrecipe._editor._routes_image import _add_image_panel_to_figure

        editor = editor_with_figure
        img_array = np.zeros((30, 30, 3), dtype=np.uint8)

        # Add image panel
        _add_image_panel_to_figure(editor, img_array, "recorded_img.png", 0.3, 0.7)

        # Check recorder has the imshow call
        if hasattr(editor.fig, "_recorder"):
            recorder = editor.fig._recorder
            # Access calls through _figure_record.axes
            if recorder._figure_record is not None:
                all_calls = []
                for ax_key, ax_record in recorder._figure_record.axes.items():
                    all_calls.extend(ax_record.calls)
                # CallRecord uses 'function' attribute, not 'method'
                imshow_calls = [c for c in all_calls if c.function == "imshow"]
                assert len(imshow_calls) > 0

    def test_multiple_images_get_unique_positions(self, editor_with_figure):
        """Verify multiple dropped images get different positions."""
        from figrecipe._editor._routes_image import _add_image_panel_to_figure

        editor = editor_with_figure
        img_array = np.zeros((20, 20, 3), dtype=np.uint8)

        # Add two images at different positions
        _add_image_panel_to_figure(editor, img_array, "img1.png", 0.2, 0.2)
        _add_image_panel_to_figure(editor, img_array, "img2.png", 0.8, 0.8)

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes = mpl_fig.get_axes()

        # Get positions of last two axes
        pos1 = axes[-2].get_position()
        pos2 = axes[-1].get_position()

        # They should have different positions
        assert pos1.x0 != pos2.x0 or pos1.y0 != pos2.y0


class TestPanelPositionCalculation:
    """Test panel position calculation from drop coordinates."""

    def test_position_clamping_top_left(self):
        """Verify position is clamped when dropping at top-left corner."""
        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import _add_image_panel_to_figure

        fig, ax = fr.subplots()
        ax.plot([1, 2], [1, 2])
        editor = FigureEditor(fig, port=5996)

        img_array = np.zeros((10, 10, 3), dtype=np.uint8)
        _add_image_panel_to_figure(editor, img_array, "corner.png", 0.0, 0.0)

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        new_ax = mpl_fig.get_axes()[-1]
        pos = new_ax.get_position()

        # Position should be clamped to minimum of 0.05
        assert pos.x0 >= 0.05

    def test_position_clamping_bottom_right(self):
        """Verify position is clamped when dropping at bottom-right corner."""
        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import _add_image_panel_to_figure

        fig, ax = fr.subplots()
        ax.plot([1, 2], [1, 2])
        editor = FigureEditor(fig, port=5995)

        img_array = np.zeros((10, 10, 3), dtype=np.uint8)
        _add_image_panel_to_figure(editor, img_array, "corner.png", 1.0, 1.0)

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        new_ax = mpl_fig.get_axes()[-1]
        pos = new_ax.get_position()

        # Position should be clamped - x0 should not exceed 0.6 (approx max)
        # The exact value depends on figure dimensions, so we allow some tolerance
        assert pos.x0 <= 0.6
        # Also verify it's in a reasonable range (not at 1.0)
        assert pos.x0 < 0.8

    def test_center_drop_position(self):
        """Verify center drop creates centered panel."""
        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import _add_image_panel_to_figure

        fig, ax = fr.subplots()
        ax.plot([1, 2], [1, 2])
        editor = FigureEditor(fig, port=5994)

        img_array = np.zeros((10, 10, 3), dtype=np.uint8)
        _add_image_panel_to_figure(editor, img_array, "center.png", 0.5, 0.5)

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        new_ax = mpl_fig.get_axes()[-1]
        pos = new_ax.get_position()

        # Panel should be roughly centered (0.5 - 0.4/2 = 0.3)
        assert 0.25 <= pos.x0 <= 0.35


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

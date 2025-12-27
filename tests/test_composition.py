#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for composition feature (Phase 1).

Tests for compose() and import_axes() functions.
"""

import matplotlib
import pytest

matplotlib.use("Agg")

import figrecipe as fr


class TestCompose:
    """Tests for compose() function."""

    @pytest.fixture
    def temp_recipes(self, tmp_path):
        """Create temporary recipe files for testing."""
        # Create first figure with a line plot
        fig1, ax1 = fr.subplots()
        ax1.plot([1, 2, 3], [1, 4, 9], id="line1")
        ax1.set_xlabel("X1")
        recipe1 = tmp_path / "fig1.yaml"
        fr.save(fig1, recipe1, validate=False, verbose=False)

        # Create second figure with a bar plot
        fig2, ax2 = fr.subplots()
        ax2.bar([1, 2, 3], [3, 1, 4], id="bar1")
        ax2.set_ylabel("Y2")
        recipe2 = tmp_path / "fig2.yaml"
        fr.save(fig2, recipe2, validate=False, verbose=False)

        return recipe1, recipe2

    def test_compose_two_figures(self, temp_recipes):
        """Compose two single-panel figures into 1x2 layout."""
        recipe1, recipe2 = temp_recipes

        fig, axes = fr.compose(
            layout=(1, 2),
            sources={
                (0, 0): recipe1,
                (0, 1): recipe2,
            },
        )

        assert fig is not None
        assert hasattr(fig, "record")
        assert len(axes) == 2

    def test_compose_creates_recording_figure(self, temp_recipes):
        """Composed figure is a RecordingFigure."""
        recipe1, recipe2 = temp_recipes

        fig, axes = fr.compose(
            layout=(1, 2),
            sources={(0, 0): recipe1, (0, 1): recipe2},
        )

        assert isinstance(fig, fr.RecordingFigure)

    def test_compose_with_specific_axes(self, tmp_path):
        """Compose selecting specific axes from multi-panel source."""
        # Create 2x2 source figure
        fig_src, axes_src = fr.subplots(2, 2)
        axes_src[0, 0].plot([1, 2], [1, 2], id="plot_a")
        axes_src[0, 1].bar([1, 2], [2, 1], id="bar_b")
        axes_src[1, 0].scatter([1, 2], [3, 4], id="scatter_c")
        recipe = tmp_path / "multi.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        # Compose using specific axes
        fig, axes = fr.compose(
            layout=(1, 2),
            sources={
                (0, 0): (recipe, "ax_0_0"),
                (0, 1): (recipe, "ax_0_1"),
            },
        )

        assert len(axes) == 2
        # Check that the correct axes were imported
        assert "ax_0_0" in fig.record.axes
        assert "ax_0_1" in fig.record.axes

    def test_compose_with_figure_record(self, tmp_path):
        """Compose using FigureRecord directly."""
        # Create and save a figure
        fig_src, ax_src = fr.subplots()
        ax_src.plot([1, 2, 3], [1, 2, 3], id="direct")
        recipe = tmp_path / "source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        # Load as FigureRecord
        record = fr.load(recipe)

        # Compose using record directly
        fig, axes = fr.compose(
            layout=(1, 1),
            sources={(0, 0): record},
        )

        assert fig is not None
        assert "ax_0_0" in fig.record.axes

    def test_compose_invalid_axes_key_raises(self, tmp_path):
        """Compose with invalid axes key raises ValueError."""
        fig_src, ax_src = fr.subplots()
        ax_src.plot([1, 2], [1, 2])
        recipe = tmp_path / "source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        with pytest.raises(ValueError, match="not found"):
            fr.compose(
                layout=(1, 1),
                sources={(0, 0): (recipe, "ax_99_99")},
            )

    def test_compose_preserves_mm_layout(self, temp_recipes):
        """Compose respects mm layout parameters."""
        recipe1, recipe2 = temp_recipes

        fig, axes = fr.compose(
            layout=(1, 2),
            sources={(0, 0): recipe1, (0, 1): recipe2},
            axes_width_mm=50,
            axes_height_mm=40,
        )

        assert fig is not None
        # Figure should have reasonable size based on mm params
        figsize = fig.fig.get_size_inches()
        assert figsize[0] > 0
        assert figsize[1] > 0


class TestImportAxes:
    """Tests for import_axes() function."""

    def test_import_into_empty_panel(self, tmp_path):
        """Import axes into existing figure's empty panel."""
        # Create source
        fig_src, ax_src = fr.subplots()
        ax_src.scatter([1, 2, 3], [1, 4, 9], id="scatter_import")
        recipe = tmp_path / "source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        # Create target with empty second panel
        fig, axes = fr.subplots(1, 2)
        axes[0].plot([1, 2], [1, 2], id="existing")

        # Import into second panel
        result = fr.import_axes(fig, (0, 1), recipe)

        assert result is not None
        assert "ax_0_1" in fig.record.axes

    def test_import_replaces_content(self, tmp_path):
        """Import replaces existing panel content."""
        # Create source
        fig_src, ax_src = fr.subplots()
        ax_src.plot([1, 2], [3, 4], id="new_line")
        recipe = tmp_path / "source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        # Create target with existing content
        fig, ax = fr.subplots()
        ax.plot([1, 2], [1, 2], id="old_line")

        # Import replaces content
        fr.import_axes(fig, (0, 0), recipe)

        # Check that the imported calls are present
        calls = fig.record.axes["ax_0_0"].calls
        call_ids = [c.id for c in calls]
        assert "new_line" in call_ids

    def test_import_specific_axes(self, tmp_path):
        """Import specific axes from multi-panel source."""
        # Create multi-panel source
        fig_src, axes_src = fr.subplots(1, 2)
        axes_src[0].plot([1, 2], [1, 2], id="left_plot")
        axes_src[1].bar([1, 2], [2, 1], id="right_bar")
        recipe = tmp_path / "multi_source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        # Create target
        fig, ax = fr.subplots()

        # Import the second panel (ax_0_1) from source
        fr.import_axes(fig, (0, 0), recipe, source_axes="ax_0_1")

        calls = fig.record.axes["ax_0_0"].calls
        call_ids = [c.id for c in calls]
        assert "right_bar" in call_ids

    def test_import_from_figure_record(self, tmp_path):
        """Import from FigureRecord object."""
        # Create and save source
        fig_src, ax_src = fr.subplots()
        ax_src.plot([1, 2, 3], [3, 2, 1], id="from_record")
        recipe = tmp_path / "source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        # Load as record
        record = fr.load(recipe)

        # Create target and import
        fig, ax = fr.subplots()
        fr.import_axes(fig, (0, 0), record)

        calls = fig.record.axes["ax_0_0"].calls
        call_ids = [c.id for c in calls]
        assert "from_record" in call_ids

    def test_import_invalid_source_raises(self):
        """Import with invalid source type raises TypeError."""
        fig, ax = fr.subplots()

        with pytest.raises(TypeError):
            fr.import_axes(fig, (0, 0), 12345)  # Invalid source

    def test_import_missing_axes_raises(self, tmp_path):
        """Import with missing source axes raises ValueError."""
        fig_src, ax_src = fr.subplots()
        ax_src.plot([1, 2], [1, 2])
        recipe = tmp_path / "source.yaml"
        fr.save(fig_src, recipe, validate=False, verbose=False)

        fig, ax = fr.subplots()

        with pytest.raises(ValueError, match="not found"):
            fr.import_axes(fig, (0, 0), recipe, source_axes="ax_99_99")


class TestComposeAndSave:
    """Integration tests for compose + save workflow."""

    def test_compose_save_reproduce(self, tmp_path):
        """Composed figure can be saved and reproduced."""
        # Create source figures
        fig1, ax1 = fr.subplots()
        ax1.plot([1, 2, 3], [1, 4, 9], id="source1")
        recipe1 = tmp_path / "src1.yaml"
        fr.save(fig1, recipe1, validate=False, verbose=False)

        fig2, ax2 = fr.subplots()
        ax2.bar([1, 2, 3], [3, 1, 4], id="source2")
        recipe2 = tmp_path / "src2.yaml"
        fr.save(fig2, recipe2, validate=False, verbose=False)

        # Compose
        composed_fig, axes = fr.compose(
            layout=(1, 2),
            sources={(0, 0): recipe1, (0, 1): recipe2},
        )

        # Save composed figure
        composed_recipe = tmp_path / "composed.yaml"
        fr.save(composed_fig, composed_recipe, validate=False, verbose=False)

        # Reproduce
        repro_fig, repro_axes = fr.reproduce(composed_recipe)

        assert repro_fig is not None
        assert "ax_0_0" in repro_fig.record.axes
        assert "ax_0_1" in repro_fig.record.axes


class TestPanelVisibility:
    """Tests for hide/show/toggle panel functions (Phase 2)."""

    def test_hide_panel(self):
        """Hidden panel not visible but data preserved."""
        fig, axes = fr.subplots(1, 2)
        axes[0].plot([1, 2], [1, 2], id="left")
        axes[1].bar([1, 2], [2, 1], id="right")

        fr.hide_panel(fig, (0, 1))

        # Check visibility flag in record
        assert not fig.record.axes["ax_0_1"].visible

        # Check matplotlib axes visibility
        assert not axes[1]._ax.get_visible()

        # Data should still be preserved
        assert len(fig.record.axes["ax_0_1"].calls) > 0

    def test_show_panel(self):
        """Show restores visibility."""
        fig, axes = fr.subplots(1, 2)
        axes[0].plot([1, 2], [1, 2])
        axes[1].plot([1, 2], [2, 1])  # Add content to create axes record

        fr.hide_panel(fig, (0, 1))
        assert not fig.record.axes["ax_0_1"].visible

        fr.show_panel(fig, (0, 1))
        assert fig.record.axes["ax_0_1"].visible
        assert axes[1]._ax.get_visible()

    def test_toggle_panel(self):
        """Toggle switches visibility state."""
        fig, ax = fr.subplots()
        ax.plot([1, 2], [1, 2])

        # First toggle: visible -> hidden
        result1 = fr.toggle_panel(fig, (0, 0))
        assert result1 is False  # Now hidden
        assert not fig.record.axes["ax_0_0"].visible

        # Second toggle: hidden -> visible
        result2 = fr.toggle_panel(fig, (0, 0))
        assert result2 is True  # Now visible
        assert fig.record.axes["ax_0_0"].visible

    def test_toggle_nonexistent_panel(self):
        """Toggle on nonexistent panel returns False."""
        fig, ax = fr.subplots()
        result = fr.toggle_panel(fig, (99, 99))
        assert result is False

    def test_visibility_serialization(self, tmp_path):
        """Visibility state persists in recipe."""
        fig, axes = fr.subplots(1, 2)
        axes[0].plot([1, 2], [1, 2], id="visible_plot")
        axes[1].bar([1, 2], [2, 1], id="hidden_bar")

        fr.hide_panel(fig, (0, 1))

        recipe = tmp_path / "hidden.yaml"
        fr.save(fig, recipe, validate=False, verbose=False)

        # Reproduce and check
        fig2, axes2 = fr.reproduce(recipe)
        assert fig2.record.axes["ax_0_0"].visible is True
        assert fig2.record.axes["ax_0_1"].visible is False

    def test_hidden_panel_not_rendered(self, tmp_path):
        """Hidden panels are skipped during reproduction."""
        fig, axes = fr.subplots(1, 2)
        axes[0].plot([1, 2], [1, 2])
        axes[1].plot([1, 2], [3, 4])

        fr.hide_panel(fig, (0, 1))

        recipe = tmp_path / "hidden.yaml"
        fr.save(fig, recipe, validate=False, verbose=False)

        # Reproduce
        fig2, axes2 = fr.reproduce(recipe)

        # Hidden panel should not be visible
        mpl_ax = axes2[1]._ax if hasattr(axes2[1], "_ax") else axes2[1]
        assert not mpl_ax.get_visible()

    def test_hide_multiple_panels(self):
        """Can hide multiple panels."""
        fig, axes = fr.subplots(2, 2)
        for i in range(2):
            for j in range(2):
                axes[i, j].plot([1, 2], [i + j, i + j + 1])

        fr.hide_panel(fig, (0, 1))
        fr.hide_panel(fig, (1, 0))

        assert fig.record.axes["ax_0_0"].visible is True
        assert fig.record.axes["ax_0_1"].visible is False
        assert fig.record.axes["ax_1_0"].visible is False
        assert fig.record.axes["ax_1_1"].visible is True


class TestVisibilityWithComposition:
    """Integration tests for visibility with composition."""

    def test_compose_then_hide(self, tmp_path):
        """Can hide panels after composition."""
        # Create sources
        fig1, ax1 = fr.subplots()
        ax1.plot([1, 2], [1, 2], id="src1")
        recipe1 = tmp_path / "src1.yaml"
        fr.save(fig1, recipe1, validate=False, verbose=False)

        fig2, ax2 = fr.subplots()
        ax2.bar([1, 2], [2, 1], id="src2")
        recipe2 = tmp_path / "src2.yaml"
        fr.save(fig2, recipe2, validate=False, verbose=False)

        # Compose
        fig, axes = fr.compose(
            layout=(1, 2),
            sources={(0, 0): recipe1, (0, 1): recipe2},
        )

        # Hide one panel
        fr.hide_panel(fig, (0, 1))

        assert fig.record.axes["ax_0_0"].visible is True
        assert fig.record.axes["ax_0_1"].visible is False

    def test_compose_hide_save_reproduce(self, tmp_path):
        """Full workflow: compose, hide, save, reproduce."""
        # Create source
        fig1, ax1 = fr.subplots()
        ax1.plot([1, 2, 3], [1, 4, 9], id="data")
        recipe1 = tmp_path / "src.yaml"
        fr.save(fig1, recipe1, validate=False, verbose=False)

        # Compose into 2x2 with only one source
        fig, axes = fr.compose(
            layout=(2, 2),
            sources={(0, 0): recipe1},
        )

        # Hide empty panels
        fr.hide_panel(fig, (0, 1))
        fr.hide_panel(fig, (1, 0))
        fr.hide_panel(fig, (1, 1))

        # Save
        output = tmp_path / "composed.yaml"
        fr.save(fig, output, validate=False, verbose=False)

        # Reproduce
        fig2, axes2 = fr.reproduce(output)

        # Check visibility states
        assert fig2.record.axes["ax_0_0"].visible is True
        assert (
            fig2.record.axes.get("ax_0_1", None) is None
            or not fig2.record.axes["ax_0_1"].visible
        )

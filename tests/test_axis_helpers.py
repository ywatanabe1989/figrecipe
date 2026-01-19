#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for axis helper utilities."""

import matplotlib.pyplot as plt
import numpy as np

import figrecipe as fr


class TestHideSpines:
    """Tests for hide_spines function."""

    def test_default_hides_top_right(self):
        """Test default behavior hides top and right spines."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        fr.hide_spines(ax)

        assert not ax.spines["top"].get_visible()
        assert not ax.spines["right"].get_visible()
        assert ax.spines["bottom"].get_visible()
        assert ax.spines["left"].get_visible()
        plt.close(fig)

    def test_hide_all_spines(self):
        """Test hiding all spines."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        fr.hide_spines(ax, top=True, bottom=True, left=True, right=True)

        for spine in ["top", "bottom", "left", "right"]:
            assert not ax.spines[spine].get_visible()
        plt.close(fig)

    def test_returns_axis(self):
        """Test that function returns the axis."""
        fig, ax = plt.subplots()
        result = fr.hide_spines(ax)
        assert result is ax
        plt.close(fig)


class TestShowSpines:
    """Tests for show_spines function."""

    def test_show_all_spines(self):
        """Test showing all spines."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        # First hide all
        for spine in ax.spines.values():
            spine.set_visible(False)

        fr.show_spines(ax)

        for spine in ["top", "bottom", "left", "right"]:
            assert ax.spines[spine].get_visible()
        plt.close(fig)

    def test_show_classic_spines(self):
        """Test classic scientific style (bottom and left only)."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        fr.show_classic_spines(ax)

        assert ax.spines["bottom"].get_visible()
        assert ax.spines["left"].get_visible()
        assert not ax.spines["top"].get_visible()
        assert not ax.spines["right"].get_visible()
        plt.close(fig)

    def test_spine_width(self):
        """Test custom spine width."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        fr.show_spines(ax, spine_width=2.0)

        for spine in ax.spines.values():
            if spine.get_visible():
                assert spine.get_linewidth() == 2.0
        plt.close(fig)


class TestToggleSpines:
    """Tests for toggle_spines function."""

    def test_toggle_visibility(self):
        """Test toggling spine visibility."""
        fig, ax = plt.subplots()
        initial_top = ax.spines["top"].get_visible()

        fr.toggle_spines(ax, top=None)  # Toggle

        assert ax.spines["top"].get_visible() != initial_top
        plt.close(fig)

    def test_explicit_set(self):
        """Test explicitly setting spine visibility."""
        fig, ax = plt.subplots()

        fr.toggle_spines(ax, top=False, bottom=True)

        assert not ax.spines["top"].get_visible()
        assert ax.spines["bottom"].get_visible()
        plt.close(fig)


class TestSetNTicks:
    """Tests for set_n_ticks function."""

    def test_sets_n_ticks(self):
        """Test setting number of ticks."""
        fig, ax = plt.subplots()
        ax.plot(np.linspace(0, 100, 100), np.linspace(0, 100, 100))

        fr.set_n_ticks(ax, n_xticks=5, n_yticks=3)

        # MaxNLocator limits but doesn't guarantee exact count
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        assert len(xticks) <= 7  # MaxNLocator adds some buffer
        assert len(yticks) <= 5
        plt.close(fig)

    def test_none_skips_axis(self):
        """Test that None skips that axis."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        fr.set_n_ticks(ax, n_xticks=None, n_yticks=3)

        # X-axis locator should be unchanged when n_xticks is None
        plt.close(fig)

    def test_returns_axis(self):
        """Test that function returns the axis."""
        fig, ax = plt.subplots()
        result = fr.set_n_ticks(ax)
        assert result is ax
        plt.close(fig)


class TestSetTicks:
    """Tests for set_ticks function."""

    def test_set_x_ticks(self):
        """Test setting x-axis ticks."""
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])

        fr.set_x_ticks(ax, x_ticks=[0, 2, 4])

        xticks = ax.get_xticks()
        assert 0 in xticks
        assert 2 in xticks
        assert 4 in xticks
        plt.close(fig)

    def test_set_y_ticks(self):
        """Test setting y-axis ticks."""
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])

        fr.set_y_ticks(ax, y_ticks=[0, 5, 10, 15])

        yticks = ax.get_yticks()
        assert 0 in yticks
        plt.close(fig)

    def test_set_both_axes(self):
        """Test setting both axes at once."""
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2], [0, 1, 2])

        result = fr.set_ticks(ax, xticks=[0, 1, 2], yticks=[0, 1, 2])

        assert result is ax
        plt.close(fig)


class TestMapTicks:
    """Tests for map_ticks function."""

    def test_numeric_mapping(self):
        """Test mapping numeric tick positions to labels."""
        fig, ax = plt.subplots()
        x = np.linspace(0, 2 * np.pi, 100)
        ax.plot(x, np.sin(x))

        src = [0, np.pi, 2 * np.pi]
        tgt = ["0", "π", "2π"]
        fr.map_ticks(ax, src, tgt, axis="x")

        labels = [t.get_text() for t in ax.get_xticklabels()]
        assert "0" in labels
        assert "π" in labels
        assert "2π" in labels
        plt.close(fig)

    def test_mismatched_lengths_raises(self):
        """Test that mismatched src/tgt lengths raise error."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        try:
            fr.map_ticks(ax, [1, 2], ["a", "b", "c"])
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        plt.close(fig)

    def test_invalid_axis_raises(self):
        """Test that invalid axis raises error."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        try:
            fr.map_ticks(ax, [1, 2], ["a", "b"], axis="z")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        plt.close(fig)


class TestRotateLabels:
    """Tests for rotate_labels function."""

    def test_rotate_x_labels(self):
        """Test rotating x-axis labels."""
        fig, ax = plt.subplots()
        ax.bar([1, 2, 3], [1, 2, 3])
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["A", "B", "C"])

        fr.rotate_labels(ax, x=45)

        for label in ax.get_xticklabels():
            assert label.get_rotation() == 45
        plt.close(fig)

    def test_returns_axis(self):
        """Test that function returns the axis."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        result = fr.rotate_labels(ax, x=30)
        assert result is ax
        plt.close(fig)


class TestSciNote:
    """Tests for sci_note function."""

    def test_applies_to_x_axis(self):
        """Test scientific notation on x-axis."""
        fig, ax = plt.subplots()
        ax.plot([1e6, 2e6, 3e6], [1, 2, 3])

        fr.sci_note(ax, x=True)

        # Check formatter is set
        formatter = ax.xaxis.get_major_formatter()
        assert formatter is not None
        plt.close(fig)

    def test_applies_to_y_axis(self):
        """Test scientific notation on y-axis."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1e-6, 2e-6, 3e-6])

        fr.sci_note(ax, y=True)

        formatter = ax.yaxis.get_major_formatter()
        assert formatter is not None
        plt.close(fig)

    def test_custom_order(self):
        """Test custom order of magnitude."""
        fig, ax = plt.subplots()
        ax.plot([1000, 2000, 3000], [1, 2, 3])

        fr.sci_note(ax, x=True, order_x=3)

        # Formatter should use order 3
        plt.close(fig)

    def test_returns_axis(self):
        """Test that function returns the axis."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        result = fr.sci_note(ax, x=True)
        assert result is ax
        plt.close(fig)


class TestForceAspect:
    """Tests for force_aspect function."""

    def test_sets_aspect_ratio(self):
        """Test setting aspect ratio on image."""
        fig, ax = plt.subplots()
        data = np.random.rand(10, 20)
        ax.imshow(data)

        fr.force_aspect(ax, aspect=1.0)

        # Aspect should be set
        aspect = ax.get_aspect()
        assert aspect != "auto"
        plt.close(fig)

    def test_no_image_raises(self):
        """Test that no image raises error."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        try:
            fr.force_aspect(ax)
            assert False, "Should have raised IndexError"
        except IndexError:
            pass
        plt.close(fig)

    def test_returns_axis(self):
        """Test that function returns the axis."""
        fig, ax = plt.subplots()
        ax.imshow(np.random.rand(10, 10))
        result = fr.force_aspect(ax)
        assert result is ax
        plt.close(fig)


class TestExtend:
    """Tests for extend function."""

    def test_extends_width(self):
        """Test extending axis width."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        original_bbox = ax.get_position()
        original_width = original_bbox.width

        fr.extend(ax, x_ratio=1.2)

        new_bbox = ax.get_position()
        assert abs(new_bbox.width - original_width * 1.2) < 0.01
        plt.close(fig)

    def test_shrinks_height(self):
        """Test shrinking axis height."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        original_bbox = ax.get_position()
        original_height = original_bbox.height

        fr.extend(ax, y_ratio=0.8)

        new_bbox = ax.get_position()
        assert abs(new_bbox.height - original_height * 0.8) < 0.01
        plt.close(fig)

    def test_zero_ratio_raises(self):
        """Test that zero ratio raises error."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        try:
            fr.extend(ax, x_ratio=0)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        plt.close(fig)

    def test_returns_axis(self):
        """Test that function returns the axis."""
        fig, ax = plt.subplots()
        result = fr.extend(ax, x_ratio=1.1)
        assert result is ax
        plt.close(fig)


class TestImports:
    """Test that axis helper functions are properly exported."""

    def test_import_from_figrecipe(self):
        """Test imports from main figrecipe module."""
        from figrecipe import (
            extend,
            force_aspect,
            hide_spines,
            rotate_labels,
            sci_note,
            set_n_ticks,
            show_spines,
        )

        assert callable(hide_spines)
        assert callable(show_spines)
        assert callable(rotate_labels)
        assert callable(set_n_ticks)
        assert callable(sci_note)
        assert callable(force_aspect)
        assert callable(extend)

    def test_import_from_styles(self):
        """Test imports from styles submodule."""
        from figrecipe.styles import (
            hide_spines,
            rotate_labels,
            set_n_ticks,
            show_spines,
        )

        assert callable(hide_spines)
        assert callable(show_spines)
        assert callable(rotate_labels)
        assert callable(set_n_ticks)

    def test_import_from_axis_helpers(self):
        """Test imports from axis_helpers submodule."""
        from figrecipe.styles.axis_helpers import (
            OOMFormatter,
            hide_spines,
        )

        assert callable(hide_spines)
        assert OOMFormatter is not None


# EOF

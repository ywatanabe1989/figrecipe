#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for plot styling utilities."""

import matplotlib.pyplot as plt
import numpy as np

import figrecipe as fr


class TestStyleBoxplot:
    """Tests for style_boxplot function."""

    def test_basic_styling(self):
        """Test basic boxplot styling."""
        fig, ax = plt.subplots()
        data = [np.random.randn(100) for _ in range(3)]
        bp = ax.boxplot(data, patch_artist=True)

        result = fr.style_boxplot(bp)

        assert result is bp
        # Check line widths were set
        for box in bp["boxes"]:
            assert box.get_linewidth() > 0
        plt.close(fig)

    def test_custom_linewidth(self):
        """Test custom line width in mm."""
        fig, ax = plt.subplots()
        data = [np.random.randn(50) for _ in range(2)]
        bp = ax.boxplot(data, patch_artist=True)

        fr.style_boxplot(bp, linewidth_mm=0.5)

        # 0.5mm should be ~1.42 points
        for whisker in bp["whiskers"]:
            lw = whisker.get_linewidth()
            assert 1.0 < lw < 2.0  # Reasonable range for 0.5mm
        plt.close(fig)

    def test_median_color(self):
        """Test custom median color."""
        fig, ax = plt.subplots()
        data = [np.random.randn(50)]
        bp = ax.boxplot(data, patch_artist=True)

        fr.style_boxplot(bp, median_color="red")

        for median in bp["medians"]:
            assert median.get_color() == "red"
        plt.close(fig)

    def test_custom_colors(self):
        """Test custom box fill colors."""
        fig, ax = plt.subplots()
        data = [np.random.randn(50) for _ in range(2)]
        bp = ax.boxplot(data, patch_artist=True)

        colors = ["#FF0000", "#00FF00"]
        fr.style_boxplot(bp, colors=colors)

        for i, box in enumerate(bp["boxes"]):
            assert box.get_facecolor()[:3] != (1, 1, 1)  # Not white
        plt.close(fig)

    def test_flier_styling(self):
        """Test outlier marker styling."""
        fig, ax = plt.subplots()
        # Create data with outliers
        data = [np.concatenate([np.random.randn(50), [10, -10]])]
        bp = ax.boxplot(data, patch_artist=True)

        fr.style_boxplot(bp, flier_size_mm=1.0)

        for flier in bp["fliers"]:
            assert flier.get_markersize() > 0
        plt.close(fig)


class TestStyleViolinplot:
    """Tests for style_violinplot function."""

    def test_basic_styling(self):
        """Test basic violin plot styling."""
        fig, ax = plt.subplots()
        data = [np.random.randn(100) for _ in range(3)]
        ax.violinplot(data)

        result = fr.style_violinplot(ax)

        assert result is ax
        plt.close(fig)

    def test_edge_color(self):
        """Test custom edge color."""
        fig, ax = plt.subplots()
        data = [np.random.randn(100)]
        ax.violinplot(data)

        fr.style_violinplot(ax, edge_color="blue")

        # Check collections have edge color set
        for collection in ax.collections:
            if hasattr(collection, "get_edgecolor"):
                ec = collection.get_edgecolor()
                assert len(ec) > 0
        plt.close(fig)

    def test_linewidth(self):
        """Test custom line width."""
        fig, ax = plt.subplots()
        data = [np.random.randn(100)]
        ax.violinplot(data)

        fr.style_violinplot(ax, linewidth_mm=0.3)

        for collection in ax.collections:
            if hasattr(collection, "get_linewidth"):
                lw = collection.get_linewidth()
                assert lw > 0
        plt.close(fig)


class TestStyleBarplot:
    """Tests for style_barplot function."""

    def test_basic_styling(self):
        """Test basic bar plot styling."""
        fig, ax = plt.subplots()
        bars = ax.bar([1, 2, 3], [4, 5, 6])

        result = fr.style_barplot(bars)

        assert result is bars
        plt.close(fig)

    def test_edge_thickness(self):
        """Test custom edge thickness."""
        fig, ax = plt.subplots()
        bars = ax.bar([1, 2, 3], [4, 5, 6])

        fr.style_barplot(bars, edge_thickness_mm=0.4)

        for bar in bars:
            lw = bar.get_linewidth()
            assert lw > 0
        plt.close(fig)

    def test_edge_color(self):
        """Test custom edge color."""
        fig, ax = plt.subplots()
        bars = ax.bar([1, 2, 3], [4, 5, 6])

        fr.style_barplot(bars, edgecolor="red")

        for bar in bars:
            ec = bar.get_edgecolor()
            # Red color check (matplotlib returns RGBA)
            assert ec[0] > 0.9  # R value high
        plt.close(fig)

    def test_multiple_edge_colors(self):
        """Test list of edge colors."""
        fig, ax = plt.subplots()
        bars = ax.bar([1, 2, 3], [4, 5, 6])

        colors = ["red", "green", "blue"]
        fr.style_barplot(bars, edgecolor=colors)

        # Each bar should have different edge color
        edge_colors = [bar.get_edgecolor() for bar in bars]
        assert edge_colors[0] != edge_colors[1]
        plt.close(fig)


class TestStyleScatter:
    """Tests for style_scatter function."""

    def test_basic_styling(self):
        """Test basic scatter plot styling."""
        fig, ax = plt.subplots()
        scatter = ax.scatter([1, 2, 3], [4, 5, 6])

        result = fr.style_scatter(scatter)

        assert result is scatter
        plt.close(fig)

    def test_size_mm(self):
        """Test custom marker size in mm."""
        fig, ax = plt.subplots()
        scatter = ax.scatter([1, 2, 3], [4, 5, 6])

        fr.style_scatter(scatter, size_mm=1.5)

        sizes = scatter.get_sizes()
        assert len(sizes) > 0
        assert sizes[0] > 0
        plt.close(fig)

    def test_edge_thickness(self):
        """Test custom edge thickness."""
        fig, ax = plt.subplots()
        scatter = ax.scatter([1, 2, 3], [4, 5, 6])

        fr.style_scatter(scatter, edge_thickness_mm=0.2)

        linewidths = scatter.get_linewidths()
        assert len(linewidths) > 0
        plt.close(fig)


class TestStyleErrorbar:
    """Tests for style_errorbar function."""

    def test_basic_styling(self):
        """Test basic errorbar styling."""
        fig, ax = plt.subplots()
        eb = ax.errorbar([1, 2, 3], [4, 5, 6], yerr=[0.5, 0.5, 0.5])

        result = fr.style_errorbar(eb)

        assert result is eb
        plt.close(fig)

    def test_thickness(self):
        """Test custom line thickness."""
        fig, ax = plt.subplots()
        eb = ax.errorbar([1, 2, 3], [4, 5, 6], yerr=[0.5, 0.5, 0.5])

        fr.style_errorbar(eb, thickness_mm=0.3)

        # Data line should have linewidth set
        if eb[0] is not None:
            lw = eb[0].get_linewidth()
            assert lw > 0
        plt.close(fig)

    def test_cap_width(self):
        """Test custom cap width."""
        fig, ax = plt.subplots()
        eb = ax.errorbar([1, 2, 3], [4, 5, 6], yerr=[0.5, 0.5, 0.5], capsize=3)

        fr.style_errorbar(eb, cap_width_mm=1.0)

        # Check caps have marker size set
        if len(eb) > 1 and eb[1] is not None:
            for cap in eb[1]:
                if cap is not None:
                    ms = cap.get_markersize()
                    assert ms > 0
        plt.close(fig)


class TestImports:
    """Test that styling functions are properly exported."""

    def test_import_from_figrecipe(self):
        """Test imports from main figrecipe module."""
        from figrecipe import (
            style_barplot,
            style_boxplot,
            style_errorbar,
            style_scatter,
            style_violinplot,
        )

        assert callable(style_boxplot)
        assert callable(style_violinplot)
        assert callable(style_barplot)
        assert callable(style_scatter)
        assert callable(style_errorbar)

    def test_import_from_styles(self):
        """Test imports from styles submodule."""
        from figrecipe.styles import (
            style_barplot,
            style_boxplot,
            style_errorbar,
            style_scatter,
            style_violinplot,
        )

        assert callable(style_boxplot)
        assert callable(style_violinplot)
        assert callable(style_barplot)
        assert callable(style_scatter)
        assert callable(style_errorbar)


# EOF

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roundtrip tests for figrecipe - verify original and reproduced figures match."""

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

# Test configurations for different plot types
ROUNDTRIP_TESTS = [
    pytest.param(
        "plot",
        lambda: (np.linspace(0, 10, 50), np.sin(np.linspace(0, 10, 50))),
        {"color": "blue", "linewidth": 2},
        id="plot",
    ),
    pytest.param(
        "scatter",
        lambda: (np.array([1, 2, 3, 4, 5]), np.array([2, 4, 1, 5, 3])),
        {"c": "red", "s": 50},
        id="scatter",
    ),
    pytest.param(
        "bar",
        lambda: (np.arange(5), np.array([3, 7, 2, 5, 8])),
        {"color": "#3498db"},
        id="bar",
    ),
    pytest.param(
        "barh",
        lambda: (np.arange(5), np.array([3, 7, 2, 5, 8])),
        {"color": "#e74c3c"},
        id="barh",
    ),
    pytest.param(
        "fill_between",
        lambda: (
            np.linspace(0, 5, 20),
            np.zeros(20),
            np.sin(np.linspace(0, 5, 20)),
        ),
        {"alpha": 0.5, "color": "green"},
        id="fill_between",
    ),
    pytest.param(
        "step",
        lambda: (np.arange(10), np.array([1, 3, 2, 4, 3, 5, 4, 6, 5, 7])),
        {"where": "mid"},
        id="step",
    ),
    pytest.param(
        "errorbar",
        lambda: (np.arange(5), np.array([2, 4, 3, 5, 4])),
        {"yerr": 0.5, "fmt": "o"},
        id="errorbar",
    ),
]


class TestRoundtrip:
    """Test that figures can be recorded, saved, and reproduced."""

    @pytest.mark.parametrize("method_name,args_func,kwargs", ROUNDTRIP_TESTS)
    def test_roundtrip_plot_types(self, method_name, args_func, kwargs):
        """Test roundtrip for various plot types."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            recipe_path = Path(tmpdir) / f"{method_name}.yaml"

            # === RECORD ===
            np.random.seed(42)
            fig, ax = ps.subplots(figsize=(6, 4))

            method = getattr(ax, method_name)
            args = args_func()
            method(*args, **kwargs, id=f"{method_name}_test")

            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            # === REPRODUCE ===
            fig2, ax2 = ps.reproduce(recipe_path)

            # Verify the reproduced figure has content
            assert fig2 is not None
            assert ax2 is not None

            # Check artists were created
            has_content = (
                len(ax2.lines) > 0
                or len(ax2.collections) > 0
                or len(ax2.patches) > 0
                or len(ax2.containers) > 0
            )
            assert has_content, f"{method_name} reproduction has no visible content"

            plt.close(fig2.fig)

    def test_roundtrip_with_decorations(self):
        """Test that decorations (labels, title, legend) are preserved."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            recipe_path = Path(tmpdir) / "decorated.yaml"

            # === RECORD ===
            fig, ax = ps.subplots()
            ax.plot([1, 2, 3], [1, 4, 9], label="quadratic")
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            ax.set_title("Test Title")
            ax.legend()

            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            # === REPRODUCE ===
            fig2, ax2 = ps.reproduce(recipe_path)

            assert ax2.get_xlabel() == "X Axis"
            assert ax2.get_ylabel() == "Y Axis"
            assert ax2.get_title() == "Test Title"

            plt.close(fig2.fig)

    def test_roundtrip_multiple_plots(self):
        """Test figure with multiple plotting calls."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            recipe_path = Path(tmpdir) / "multi.yaml"

            x = np.linspace(0, 10, 50)

            # === RECORD ===
            fig, ax = ps.subplots()
            ax.plot(x, np.sin(x), color="blue", id="sin")
            ax.plot(x, np.cos(x), color="red", id="cos")
            ax.scatter(x[::5], np.sin(x[::5]), s=50, id="points")

            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            # === REPRODUCE ===
            fig2, ax2 = ps.reproduce(recipe_path)

            # Should have 2 lines and 1 collection (scatter)
            assert len(ax2.lines) >= 2
            assert len(ax2.collections) >= 1

            plt.close(fig2.fig)

    def test_roundtrip_data_integrity(self):
        """Test that data values are preserved in roundtrip."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            recipe_path = Path(tmpdir) / "data_check.yaml"

            x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
            y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])

            # === RECORD ===
            fig, ax = ps.subplots()
            ax.plot(x, y, id="linear")

            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            # === REPRODUCE ===
            fig2, ax2 = ps.reproduce(recipe_path)

            # Check data matches
            line = ax2.lines[0]
            np.testing.assert_array_almost_equal(line.get_xdata(), x)
            np.testing.assert_array_almost_equal(line.get_ydata(), y)

            plt.close(fig2.fig)

    def test_roundtrip_large_array(self):
        """Test roundtrip with large arrays (saved to .npy)."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            recipe_path = Path(tmpdir) / "large.yaml"

            # Large arrays (> 100 elements)
            x = np.linspace(0, 100, 500)
            y = np.sin(x) * np.exp(-x / 50)

            # === RECORD ===
            fig, ax = ps.subplots()
            ax.plot(x, y, id="damped_sine")

            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            # Check data files were created (CSV by default)
            data_dir = Path(tmpdir) / "large_data"
            assert data_dir.exists()
            assert len(list(data_dir.glob("*.csv"))) > 0

            # === REPRODUCE ===
            fig2, ax2 = ps.reproduce(recipe_path)

            # Check data matches
            line = ax2.lines[0]
            np.testing.assert_array_almost_equal(line.get_xdata(), x)
            np.testing.assert_array_almost_equal(line.get_ydata(), y, decimal=5)

            plt.close(fig2.fig)


class TestPixelComparison:
    """Test pixel-level comparison utilities."""

    def test_identical_images(self):
        """Test that identical images are detected as identical."""
        try:
            from figrecipe._utils._image_diff import compare_images
        except ImportError:
            pytest.skip("PIL not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            img1 = Path(tmpdir) / "img1.png"
            img2 = Path(tmpdir) / "img2.png"

            # Create identical figures
            for img_path in [img1, img2]:
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot([1, 2, 3], [1, 2, 3])
                fig.savefig(img_path, dpi=100)
                plt.close(fig)

            result = compare_images(img1, img2)
            assert result["identical"]
            assert result["mse"] == 0

    def test_different_images(self):
        """Test that different images are detected as different."""
        try:
            from figrecipe._utils._image_diff import compare_images
        except ImportError:
            pytest.skip("PIL not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            img1 = Path(tmpdir) / "img1.png"
            img2 = Path(tmpdir) / "img2.png"

            # Create different figures
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([1, 2, 3], [1, 2, 3], color="blue")
            fig.savefig(img1, dpi=100)
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([1, 2, 3], [3, 2, 1], color="red")
            fig.savefig(img2, dpi=100)
            plt.close(fig)

            result = compare_images(img1, img2)
            assert not result["identical"]
            assert result["mse"] > 0

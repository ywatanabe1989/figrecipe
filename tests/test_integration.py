#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration tests for figrecipe."""

import tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing

import matplotlib.pyplot as plt
import numpy as np
import pytest


class TestSubplotsAndSave:
    """Tests for subplots() and save() functions."""

    def test_subplots_single(self):
        """Test creating a single subplot."""
        import figrecipe as ps

        fig, ax = ps.subplots()

        assert hasattr(fig, '_recorder')
        assert hasattr(ax, '_ax')

        plt.close(fig.fig)

    def test_subplots_multiple(self):
        """Test creating multiple subplots."""
        import figrecipe as ps

        fig, axes = ps.subplots(2, 2)

        assert len(axes) == 2
        assert len(axes[0]) == 2

        plt.close(fig.fig)

    def test_plot_and_save(self):
        """Test plotting and saving a recipe."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            x = np.linspace(0, 10, 50)
            y = np.sin(x)

            fig, ax = ps.subplots()
            ax.plot(x, y, color='red', linewidth=2)

            recipe_path = Path(tmpdir) / "test_recipe.png"
            img_path, yaml_path, result = ps.save(fig, recipe_path, validate=False)

            assert img_path.exists()
            assert yaml_path.exists()
            assert img_path.suffix == ".png"
            assert yaml_path.suffix == ".yaml"

            plt.close(fig.fig)

    def test_save_with_custom_id(self):
        """Test saving with custom call ID."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = ps.subplots()
            ax.plot([1, 2, 3], [4, 5, 6], id='my_line')

            recipe_path = Path(tmpdir) / "custom_id.png"
            img_path, yaml_path, result = ps.save(fig, recipe_path, validate=False)

            # Check the recipe contains our custom ID
            info = ps.info(yaml_path)
            call_ids = [c['id'] for c in info['calls']]
            assert 'my_line' in call_ids

            plt.close(fig.fig)


class TestReproduce:
    """Tests for reproduce() function."""

    def test_reproduce_simple(self):
        """Test reproducing a simple figure."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            x = np.array([1, 2, 3, 4, 5])
            y = np.array([2, 4, 1, 5, 3])

            fig1, ax1 = ps.subplots()
            ax1.plot(x, y, color='blue')

            recipe_path = Path(tmpdir) / "simple.yaml"
            ps.save(fig1, recipe_path, validate=False)
            plt.close(fig1.fig)

            # Reproduce
            fig2, ax2 = ps.reproduce(recipe_path)

            # Check figure was created
            assert fig2 is not None
            assert ax2 is not None

            plt.close(fig2)

    def test_reproduce_multiple_calls(self):
        """Test reproducing figure with multiple calls."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            fig1, ax1 = ps.subplots()
            ax1.plot([1, 2, 3], [1, 2, 3], color='red')
            ax1.scatter([1, 2, 3], [3, 2, 1], s=50)

            recipe_path = Path(tmpdir) / "multi.yaml"
            ps.save(fig1, recipe_path, validate=False)
            plt.close(fig1.fig)

            # Reproduce
            fig2, ax2 = ps.reproduce(recipe_path)

            # Check both artists were created
            assert len(ax2.lines) >= 1
            assert len(ax2.collections) >= 1

            plt.close(fig2)

    def test_reproduce_with_decorations(self):
        """Test reproducing figure with decorations."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            fig1, ax1 = ps.subplots()
            ax1.plot([1, 2, 3], [1, 2, 3])
            ax1.set_xlabel('X Label')
            ax1.set_ylabel('Y Label')
            ax1.set_title('Title')

            recipe_path = Path(tmpdir) / "decorated.yaml"
            ps.save(fig1, recipe_path, validate=False)
            plt.close(fig1.fig)

            # Reproduce
            fig2, ax2 = ps.reproduce(recipe_path)

            assert ax2.get_xlabel() == 'X Label'
            assert ax2.get_ylabel() == 'Y Label'
            assert ax2.get_title() == 'Title'

            plt.close(fig2)


class TestInfo:
    """Tests for info() function."""

    def test_info_basic(self):
        """Test getting recipe info."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            fig, ax = ps.subplots(figsize=(10, 6))
            ax.plot([1, 2, 3], [4, 5, 6], id='test_plot')

            recipe_path = Path(tmpdir) / "info_test.yaml"
            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            info = ps.info(recipe_path)

            assert 'id' in info
            assert 'created' in info
            assert info['figsize'] == (10, 6)
            assert info['n_axes'] == 1
            assert len(info['calls']) >= 1


class TestLargeArrays:
    """Tests for handling large arrays."""

    def test_large_array_saved_to_file(self):
        """Test that large arrays are saved to separate files."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create large arrays (> INLINE_THRESHOLD)
            x = np.linspace(0, 100, 1000)
            y = np.sin(x)

            fig, ax = ps.subplots()
            ax.plot(x, y)

            recipe_path = Path(tmpdir) / "large.yaml"
            ps.save(fig, recipe_path, validate=False)
            plt.close(fig.fig)

            # Check that data directory was created
            data_dir = Path(tmpdir) / "large_data"
            assert data_dir.exists()

            # Check that data files were created (CSV by default)
            data_files = list(data_dir.glob("*.csv"))
            assert len(data_files) > 0

    def test_large_array_reproduced_correctly(self):
        """Test that large arrays are reproduced correctly."""
        import figrecipe as ps

        with tempfile.TemporaryDirectory() as tmpdir:
            x = np.linspace(0, 100, 500)
            y = np.sin(x)

            fig1, ax1 = ps.subplots()
            ax1.plot(x, y, color='green')

            recipe_path = Path(tmpdir) / "large_repro.yaml"
            ps.save(fig1, recipe_path, validate=False)
            plt.close(fig1.fig)

            # Reproduce
            fig2, ax2 = ps.reproduce(recipe_path)

            # Check that line data matches
            line = ax2.lines[0]
            xdata, ydata = line.get_xdata(), line.get_ydata()

            np.testing.assert_array_almost_equal(xdata, x)
            np.testing.assert_array_almost_equal(ydata, y)

            plt.close(fig2)

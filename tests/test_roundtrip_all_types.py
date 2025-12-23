#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roundtrip tests for all plotting methods.

Tests each supported plotting method with save/reproduce cycle.
Uses _dev.PLOTTERS as single source of truth for available plotters.
"""

import sys
import tempfile
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import figrecipe as fr
from figrecipe._dev import PLOTTERS, list_plotters
from figrecipe._utils._image_diff import compare_images


class TestRoundtripAllPlotters:
    """Roundtrip tests for all plotting methods."""

    @pytest.fixture
    def rng(self):
        """Random number generator with fixed seed."""
        return np.random.default_rng(42)

    @pytest.fixture
    def tmpdir(self):
        """Temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.mark.parametrize("plot_type", list_plotters())
    def test_roundtrip(self, plot_type, rng, tmpdir):
        """Test that plot type can be saved and reproduced."""
        plotter = PLOTTERS[plot_type]

        # Create original figure
        fig, ax = plotter(fr, rng)

        # Save
        recipe_path = tmpdir / f"{plot_type}.yaml"
        fr.save(fig, recipe_path, validate=False)
        plt.close(fig.fig)

        # Reproduce
        fig2, ax2 = fr.reproduce(recipe_path)

        # Basic checks
        assert fig2 is not None
        assert ax2 is not None

        plt.close(fig2.fig)

    @pytest.mark.parametrize("plot_type", list_plotters())
    def test_roundtrip_pixel_match(self, plot_type, rng, tmpdir):
        """Test that reproduced figure matches original within threshold."""
        plotter = PLOTTERS[plot_type]

        # Create original figure
        fig, ax = plotter(fr, rng)

        # Save original image
        original_path = tmpdir / f"{plot_type}_original.png"
        fig.fig.savefig(original_path, dpi=100, bbox_inches="tight", facecolor="white")

        # Save recipe
        recipe_path = tmpdir / f"{plot_type}.yaml"
        fr.save(fig, recipe_path, validate=False)
        plt.close(fig.fig)

        # Reproduce
        fig2, ax2 = fr.reproduce(recipe_path)

        # Save reproduced image
        reproduced_path = tmpdir / f"{plot_type}_reproduced.png"
        fig2.fig.savefig(
            reproduced_path, dpi=100, bbox_inches="tight", facecolor="white"
        )
        plt.close(fig2.fig)

        # Compare images
        comparison = compare_images(original_path, reproduced_path)

        # Assert low MSE (allowing for minor rendering differences)
        assert (
            comparison["mse"] < 1.0
        ), f"{plot_type}: MSE {comparison['mse']:.4f} exceeds threshold"


def run_manual_test():
    """Run tests manually and print summary."""
    from figrecipe._utils._image_diff import create_comparison_figure

    print("=" * 60)
    print("Roundtrip Tests for All Plotting Methods")
    print("=" * 60)

    output_dir = Path(__file__).parent.parent / "outputs" / "roundtrip_tests"
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(42)
    results = {}

    for plot_type in list_plotters():
        print(f"\nTesting {plot_type}()...", end=" ")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                plotter = PLOTTERS[plot_type]

                # Create original
                fig, ax = plotter(fr, rng)

                # Save paths
                original_path = output_dir / f"{plot_type}_original.png"
                recipe_path = output_dir / f"{plot_type}_recipe.yaml"
                reproduced_path = output_dir / f"{plot_type}_reproduced.png"
                comparison_path = output_dir / f"{plot_type}_comparison.png"

                # Save original
                fig.fig.savefig(
                    original_path, dpi=100, bbox_inches="tight", facecolor="white"
                )
                fr.save(fig, recipe_path, validate=False)
                plt.close(fig.fig)

                # Reproduce
                fig2, ax2 = fr.reproduce(recipe_path)
                fig2.fig.savefig(
                    reproduced_path, dpi=100, bbox_inches="tight", facecolor="white"
                )
                plt.close(fig2.fig)

                # Compare
                comparison = compare_images(original_path, reproduced_path)
                create_comparison_figure(
                    original_path, reproduced_path, comparison_path, plot_type
                )

                if comparison["mse"] < 1.0:
                    print(f"PASS (MSE: {comparison['mse']:.4f})")
                    results[plot_type] = {"status": "PASS", "mse": comparison["mse"]}
                else:
                    print(f"DIFF (MSE: {comparison['mse']:.4f})")
                    results[plot_type] = {"status": "DIFF", "mse": comparison["mse"]}

        except Exception as e:
            print(f"ERROR: {e}")
            results[plot_type] = {"status": "ERROR", "error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r.get("status") == "PASS")
    diffed = sum(1 for r in results.values() if r.get("status") == "DIFF")
    errors = sum(1 for r in results.values() if r.get("status") == "ERROR")
    total = len(results)

    print(f"PASS:  {passed}/{total}")
    print(f"DIFF:  {diffed}/{total}")
    print(f"ERROR: {errors}/{total}")

    if errors > 0:
        print("\nErrors:")
        for name, r in results.items():
            if r.get("status") == "ERROR":
                print(f"  {name}: {r.get('error')}")

    print(f"\nOutput: {output_dir.absolute()}")

    return results


if __name__ == "__main__":
    run_manual_test()

# EOF

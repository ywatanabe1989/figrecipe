#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 23:07:48 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/roundtrip_all_types.py


"""
Programmatic Roundtrip Test for All Plotting Types
===================================================
Tests each supported plotting method with pixel-level comparison.
"""

import sys

sys.path.insert(0, "../src")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

import figrecipe as fr
from figrecipe._utils._image_diff import compare_images
from figrecipe._utils._image_diff import create_comparison_figure


# Define test cases for each plotting type
PLOT_TESTS = {
    "plot": {
        "args": lambda: (
            np.linspace(0, 10, 50),
            np.sin(np.linspace(0, 10, 50)),
        ),
        "kwargs": {"color": "blue", "linewidth": 2, "label": "sin(x)"},
    },
    "scatter": {
        "args": lambda: (np.random.randn(30), np.random.randn(30)),
        "kwargs": {"c": "red", "s": 50, "alpha": 0.7},
    },
    "bar": {
        "args": lambda: (np.arange(5), [3, 7, 2, 5, 8]),
        "kwargs": {"color": "#3498db", "edgecolor": "black"},
    },
    "barh": {
        "args": lambda: (np.arange(5), [3, 7, 2, 5, 8]),
        "kwargs": {"color": "#e74c3c"},
    },
    "hist": {
        "args": lambda: (np.random.randn(500),),
        "kwargs": {"bins": 20, "color": "#2ecc71", "alpha": 0.7},
    },
    "fill_between": {
        "args": lambda: (
            np.linspace(0, 10, 50),
            np.sin(np.linspace(0, 10, 50)) - 0.5,
            np.sin(np.linspace(0, 10, 50)) + 0.5,
        ),
        "kwargs": {"alpha": 0.5, "color": "purple"},
    },
    "stem": {
        "args": lambda: (np.arange(10), np.random.rand(10)),
        "kwargs": {},
    },
    "step": {
        "args": lambda: (np.arange(10), np.random.rand(10)),
        "kwargs": {"where": "mid", "color": "green"},
    },
    "errorbar": {
        "args": lambda: (np.arange(5), [2, 4, 3, 5, 4]),
        "kwargs": {"yerr": 0.5, "fmt": "o-", "capsize": 5},
    },
    "fill": {
        "args": lambda: ([0, 1, 2, 1, 0], [0, 1, 0, -1, 0]),
        "kwargs": {"color": "orange", "alpha": 0.5},
    },
    "axhline": {
        "args": lambda: (),
        "kwargs": {"y": 0.5, "color": "red", "linestyle": "--"},
    },
    "axvline": {
        "args": lambda: (),
        "kwargs": {"x": 0.5, "color": "blue", "linestyle": ":"},
    },
}


def run_roundtrip_test(
    plot_type: str, test_config: dict, output_dir: Path
) -> dict:
    """Run a single roundtrip test.

    Parameters
    ----------
    plot_type : str
        Name of the plotting method.
    test_config : dict
        Test configuration with 'args' and 'kwargs'.
    output_dir : Path
        Output directory for files.

    Returns
    -------
    dict
        Test results.
    """
    np.random.seed(42)  # Reproducibility

    # Paths
    original_path = output_dir / f"{plot_type}_original.png"
    recipe_path = output_dir / f"{plot_type}_recipe.yaml"
    reproduced_path = output_dir / f"{plot_type}_reproduced.png"
    comparison_path = output_dir / f"{plot_type}_comparison.png"

    try:
        # === ORIGINAL ===
        fig, ax = fr.subplots(figsize=(6, 4))
        method = getattr(ax, plot_type)
        args = test_config["args"]()
        kwargs = test_config["kwargs"].copy()
        kwargs["id"] = f"{plot_type}_test"
        method(*args, **kwargs)
        ax.set_title(f"{plot_type}()")

        fig.fig.savefig(
            original_path, dpi=100, bbox_inches="tight", facecolor="white"
        )
        fr.save(fig, recipe_path)
        plt.close(fig.fig)

        # === REPRODUCED ===
        fig2, ax2 = fr.reproduce(recipe_path)
        fig2.savefig(
            reproduced_path, dpi=100, bbox_inches="tight", facecolor="white"
        )
        plt.close(fig2)

        # === COMPARE ===
        comparison = compare_images(original_path, reproduced_path)
        create_comparison_figure(
            original_path, reproduced_path, comparison_path, plot_type
        )

        return {
            "status": "PASS" if comparison["mse"] < 1.0 else "DIFF",
            "mse": comparison["mse"],
            "identical": comparison["identical"],
            "error": None,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "mse": None,
            "identical": False,
            "error": str(e),
        }


def main():
    print("=" * 60)
    print("Programmatic Roundtrip Test for All Plotting Types")
    print("=" * 60)

    output_dir = Path(__file__).parent.parent / "outputs" / "roundtrip_tests"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for plot_type, config in PLOT_TESTS.items():
        print(f"\nTesting {plot_type}()...", end=" ")
        result = run_roundtrip_test(plot_type, config, output_dir)
        results[plot_type] = result

        if result["status"] == "PASS":
            print(f"PASS (MSE: {result['mse']:.4f})")
        elif result["status"] == "DIFF":
            print(f"DIFF (MSE: {result['mse']:.4f})")
        else:
            print(f"ERROR: {result['error']}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    diffed = sum(1 for r in results.values() if r["status"] == "DIFF")
    errors = sum(1 for r in results.values() if r["status"] == "ERROR")

    print(f"PASS:  {passed}/{len(results)}")
    print(f"DIFF:  {diffed}/{len(results)}")
    print(f"ERROR: {errors}/{len(results)}")

    if errors > 0:
        print("\nErrors:")
        for name, r in results.items():
            if r["status"] == "ERROR":
                print(f"  {name}: {r['error']}")

    print(f"\nOutput: {output_dir.absolute()}")


if __name__ == "__main__":
    main()

# EOF

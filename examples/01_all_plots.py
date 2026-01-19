#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-11 02:22:55 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/01_all_plots.py


"""Simple demo script to generate all supported plot types.

Uses fr.run_all_demos() to generate individual plot files with proper
mm-based layout and auto-cropping.

Outputs saved to ./01_all_plots_out/plot_*.png

See 02_composition.py for combining all plots into a single figure.
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import figrecipe as fr
from figrecipe._dev import run_all_demos

OUTPUT_DIR = Path(__file__.replace(".py", "_out"))


def main():
    """Run all demos and save to output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load SCITEX style (40x28mm axes, 1mm margins after crop)
    fr.load_style("SCITEX")

    print("Generating all demo plots...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Run all demos using the built-in function
    results = run_all_demos(fr, output_dir=OUTPUT_DIR, show=False, verbose=True)

    # Summary
    print()
    successes = sum(1 for r in results.values() if r["success"])
    failures = [name for name, r in results.items() if not r["success"]]
    print(f"Generated {successes}/{len(results)} plots successfully")

    if failures:
        print(f"Failed plots ({len(failures)}):")
        for name in failures:
            print(f"  - {name}: {results[name]['error']}")


if __name__ == "__main__":
    main()

# EOF

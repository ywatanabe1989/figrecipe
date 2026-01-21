#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: CSV Column Workflow for MCP Integration
================================================

This example demonstrates the RECOMMENDED workflow for using figrecipe
with MCP tools:

1. Analysis code writes data to CSV files
2. MCP plot tool references CSV columns (not inline arrays)
3. Figures are created with full reproducibility

This pattern enables:
- Separation of data from visualization
- Easy data updates without changing plot spec
- Better integration between analysis code and MCP visualization
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd

# Setup output directory
OUTPUT_DIR = Path(__file__).parent / "05_csv_workflow_out"
OUTPUT_DIR.mkdir(exist_ok=True)
os.chdir(OUTPUT_DIR)


def step1_generate_data():
    """Step 1: Analysis code generates CSV data."""
    print("=" * 60)
    print("Step 1: Generate CSV data (simulating analysis code)")
    print("=" * 60)

    # Simulate experiment data
    np.random.seed(42)
    n_points = 50

    time = np.linspace(0, 10, n_points)
    signal = np.sin(time) * np.exp(-time / 5) + np.random.normal(0, 0.1, n_points)
    fitted = np.sin(time) * np.exp(-time / 5)

    # Save to CSV
    df = pd.DataFrame(
        {"time_sec": time, "measured_signal": signal, "fitted_curve": fitted}
    )
    df.to_csv("experiment_data.csv", index=False)
    print(f"Created: experiment_data.csv ({len(df)} rows)")
    print(f"Columns: {list(df.columns)}")

    # Also create group comparison data
    groups = []
    values = []
    for i, (name, mean, std) in enumerate(
        [("Control", 10, 2), ("Treatment A", 15, 2.5), ("Treatment B", 18, 3)]
    ):
        n = 30
        groups.extend([name] * n)
        values.extend(np.random.normal(mean, std, n).tolist())

    df_groups = pd.DataFrame({"group": groups, "measurement": values})
    df_groups.to_csv("group_comparison.csv", index=False)
    print(f"Created: group_comparison.csv ({len(df_groups)} rows)")

    return "experiment_data.csv", "group_comparison.csv"


def step2_create_mcp_spec():
    """Step 2: Create MCP-compatible plot specification using CSV columns."""
    print("\n" + "=" * 60)
    print("Step 2: Create MCP plot specification (CSV column references)")
    print("=" * 60)

    # This is the spec format used by MCP plt_plot tool
    spec_line_plot = {
        "figure": {"width_mm": 80, "height_mm": 60, "style": "SCITEX"},
        "plots": [
            {
                "type": "scatter",
                "data_file": "experiment_data.csv",  # CSV file path
                "x": "time_sec",  # Column name (string, not array!)
                "y": "measured_signal",  # Column name
                "color": "blue",
                "alpha": 0.6,
                "label": "Measured",
            },
            {
                "type": "line",
                "data_file": "experiment_data.csv",
                "x": "time_sec",
                "y": "fitted_curve",
                "color": "red",
                "label": "Fitted",
            },
        ],
        "xlabel": "Time (s)",
        "ylabel": "Signal (mV)",
        "title": "Damped Oscillation",
        "legend": True,
    }

    print("Spec for line plot:")
    print("  data_file: experiment_data.csv")
    print("  x column: time_sec")
    print("  y columns: measured_signal, fitted_curve")

    return spec_line_plot


def step3_create_figure_from_spec(spec):
    """Step 3: Create figure using the spec (like MCP would do)."""
    print("\n" + "=" * 60)
    print("Step 3: Create figure from spec (MCP-style)")
    print("=" * 60)

    from figrecipe._api._plot import create_figure_from_spec

    result = create_figure_from_spec(
        spec=spec, output_path="csv_workflow_demo.png", dpi=300, save_recipe=True
    )

    print(f"Created: {result['image_path']}")
    print(f"Recipe:  {result['recipe_path']}")

    return result


def step4_demonstrate_python_api():
    """Step 4: Alternative - Direct Python API with CSV."""
    print("\n" + "=" * 60)
    print("Step 4: Alternative - Direct Python API")
    print("=" * 60)

    import figrecipe as fr

    # Load CSV data
    df = pd.read_csv("experiment_data.csv")

    # Create figure with standard matplotlib API
    fig, ax = fr.subplots(axes_width_mm=80, axes_height_mm=60)

    ax.scatter(
        df["time_sec"],
        df["measured_signal"],
        color="blue",
        alpha=0.6,
        label="Measured",
    )
    ax.plot(df["time_sec"], df["fitted_curve"], color="red", label="Fitted")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal (mV)")
    ax.set_title("Python API Demo")
    ax.legend()

    # Save creates: image + recipe + data CSVs
    fr.save(fig, "python_api_demo.png")
    print("Created: python_api_demo.png + python_api_demo.yaml + python_api_demo_data/")


def step5_show_output_structure():
    """Step 5: Show the output file structure."""
    print("\n" + "=" * 60)
    print("Step 5: Output file structure")
    print("=" * 60)

    for f in sorted(OUTPUT_DIR.iterdir()):
        if f.is_dir():
            print(f"  {f.name}/")
            for sub in sorted(f.iterdir()):
                print(f"    {sub.name}")
        else:
            size = f.stat().st_size
            print(f"  {f.name} ({size:,} bytes)")


def main():
    """Run the complete CSV workflow demonstration."""
    print("\nFigRecipe CSV Workflow Demo")
    print("===========================\n")
    print("This demonstrates the RECOMMENDED pattern:")
    print("  Analysis code → CSV → MCP plot spec → Figure\n")

    # Step 1: Generate data (like analysis code would)
    step1_generate_data()

    # Step 2: Create MCP-compatible spec with CSV references
    spec = step2_create_mcp_spec()

    # Step 3: Create figure from spec (MCP-style)
    step3_create_figure_from_spec(spec)

    # Step 4: Alternative Python API
    step4_demonstrate_python_api()

    # Step 5: Show output structure
    step5_show_output_structure()

    print("\n" + "=" * 60)
    print("SUMMARY: CSV Workflow Benefits")
    print("=" * 60)
    print("1. Data separate from visualization spec")
    print("2. Easy to update data without changing spec")
    print("3. Better integration with analysis code")
    print("4. MCP can visualize any CSV file")
    print("5. Full reproducibility via YAML recipes")

    return 0


if __name__ == "__main__":
    main()

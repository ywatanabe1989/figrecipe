#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract command - Extract plotted data from recipes."""

import json
from pathlib import Path
from typing import Optional

import click


@click.command()
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output directory for extracted data.",
)
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["csv", "npz", "json"]),
    default="csv",
    help="Data format (default: csv).",
)
@click.option(
    "--axes",
    type=str,
    help="Specific axes to extract (e.g., ax_0_0).",
)
def extract(
    source: str,
    output: Optional[str],
    fmt: str,
    axes: Optional[str],
) -> None:
    """Extract plotted data arrays from a recipe.

    SOURCE is the path to a .yaml recipe file.
    """

    from .. import extract_data

    source_path = Path(source)

    try:
        data = extract_data(source_path)
    except Exception as e:
        raise click.ClickException(f"Failed to extract data: {e}") from e

    if not data:
        click.echo("No data found in recipe.")
        return

    # Determine output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = source_path.parent / f"{source_path.stem}_data"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Export data
    for call_id, call_data in data.items():
        if axes and not call_id.startswith(axes):
            continue

        if fmt == "json":
            _save_json(output_dir / f"{call_id}.json", call_data)
        elif fmt == "npz":
            _save_npz(output_dir / f"{call_id}.npz", call_data)
        else:  # csv
            _save_csv(output_dir / f"{call_id}.csv", call_data)

        click.echo(f"Extracted: {call_id}")

    click.echo(f"\nData saved to: {output_dir}")


def _save_json(path: Path, data: dict) -> None:
    """Save data as JSON."""
    import numpy as np

    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    with open(path, "w") as f:
        json.dump({k: convert(v) for k, v in data.items()}, f, indent=2)


def _save_npz(path: Path, data: dict) -> None:
    """Save data as NPZ."""
    import numpy as np

    np.savez(path, **data)


def _save_csv(path: Path, data: dict) -> None:
    """Save data as CSV."""
    import numpy as np

    # Try to create a table from the data
    arrays = {k: np.asarray(v) for k, v in data.items() if hasattr(v, "__len__")}

    if not arrays:
        return

    # Find max length
    max_len = max(len(a.flatten()) for a in arrays.values())

    with open(path, "w") as f:
        # Header
        f.write(",".join(arrays.keys()) + "\n")

        # Data rows
        for i in range(max_len):
            row = []
            for arr in arrays.values():
                flat = arr.flatten()
                if i < len(flat):
                    row.append(str(flat[i]))
                else:
                    row.append("")
            f.write(",".join(row) + "\n")

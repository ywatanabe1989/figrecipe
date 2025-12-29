#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reproduce command - Recreate figure from recipe."""

from pathlib import Path
from typing import Optional

import click


@click.command()
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output path for the reproduced figure.",
)
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["png", "pdf", "svg"]),
    default="png",
    help="Output format (default: png).",
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="DPI for raster output (default: 300).",
)
@click.option(
    "--show",
    is_flag=True,
    help="Display the figure interactively.",
)
def reproduce(
    source: str,
    output: Optional[str],
    fmt: str,
    dpi: int,
    show: bool,
) -> None:
    """Reproduce a figure from a YAML recipe.

    SOURCE is the path to a .yaml recipe file or bundle directory.
    """
    import matplotlib.pyplot as plt

    from .. import reproduce as fr_reproduce

    source_path = Path(source)

    # Reproduce the figure
    try:
        fig, axes = fr_reproduce(source_path)
    except Exception as e:
        raise click.ClickException(f"Failed to reproduce: {e}") from e

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = source_path.with_suffix(f".reproduced.{fmt}")

    # Save or show
    if show:
        plt.show()
    else:
        fig.savefig(output_path, dpi=dpi, format=fmt)
        click.echo(f"Saved: {output_path}")

    # Close the figure (handle both regular and Recording figures)
    try:
        plt.close(fig)
    except TypeError:
        # RecordingFigure wrapper - close all instead
        plt.close("all")

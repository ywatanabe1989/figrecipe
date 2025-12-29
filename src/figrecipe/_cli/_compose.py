#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compose command - Combine multiple figures."""

from pathlib import Path
from typing import Optional, Tuple

import click


@click.command()
@click.argument("sources", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    required=True,
    help="Output path for composed figure.",
)
@click.option(
    "--layout",
    type=click.Choice(["horizontal", "vertical", "grid"]),
    default="horizontal",
    help="Layout arrangement (default: horizontal).",
)
@click.option(
    "--cols",
    type=int,
    help="Number of columns for grid layout.",
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="DPI for output (default: 300).",
)
def compose(
    sources: Tuple[str, ...],
    output: str,
    layout: str,
    cols: Optional[int],
    dpi: int,
) -> None:
    """Compose multiple figures into one.

    SOURCES are paths to .yaml recipe files or bundle directories.
    """
    from .. import compose as fr_compose
    from .. import reproduce, save

    if len(sources) < 2:
        raise click.ClickException("At least 2 source figures required.")

    source_paths = [Path(s) for s in sources]
    output_path = Path(output)

    # Determine grid dimensions
    n = len(sources)
    if layout == "horizontal":
        nrows, ncols = 1, n
    elif layout == "vertical":
        nrows, ncols = n, 1
    else:  # grid
        if cols:
            ncols = cols
            nrows = (n + cols - 1) // cols
        else:
            # Auto-determine roughly square grid
            import math

            ncols = math.ceil(math.sqrt(n))
            nrows = math.ceil(n / ncols)

    # Reproduce and compose figures
    try:
        figures = []
        for src in source_paths:
            fig, _ = reproduce(src)
            figures.append(fig)

        composed = fr_compose(*figures, nrows=nrows, ncols=ncols)
        save(composed, output_path, dpi=dpi)

        click.echo(f"Composed {len(figures)} figures: {output_path}")

    except Exception as e:
        raise click.ClickException(f"Composition failed: {e}") from e

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""convert command - Convert between formats."""

from pathlib import Path
from typing import Optional

import click


@click.command()
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["png", "pdf", "svg", "yaml"]),
    required=True,
    help="Target format.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output path.",
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="DPI for raster output (default: 300).",
)
def convert(
    source: str,
    fmt: str,
    output: Optional[str],
    dpi: int,
) -> None:
    """Convert between figure formats.

    SOURCE is a .yaml recipe or image file.
    """
    source_path = Path(source)

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = source_path.with_suffix(f".{fmt}")

    # Handle different source types
    if source_path.suffix in [".yaml", ".yml"]:
        _convert_from_recipe(source_path, output_path, fmt, dpi)
    elif source_path.suffix in [".png", ".pdf", ".svg"]:
        _convert_image(source_path, output_path, fmt, dpi)
    else:
        raise click.ClickException(f"Unsupported source format: {source_path.suffix}")


def _convert_from_recipe(source: Path, output: Path, fmt: str, dpi: int) -> None:
    """Convert from YAML recipe to image format."""
    import matplotlib.pyplot as plt

    from .. import reproduce

    try:
        fig, _ = reproduce(source)

        if fmt == "yaml":
            # Already have YAML, just copy
            import shutil

            shutil.copy(source, output)
        else:
            fig.savefig(output, dpi=dpi, format=fmt)

        # Close the figure (handle both regular and Recording figures)
        try:
            plt.close(fig)
        except TypeError:
            plt.close("all")

        click.echo(f"Converted: {output}")

    except Exception as e:
        raise click.ClickException(f"Conversion failed: {e}") from e


def _convert_image(source: Path, output: Path, fmt: str, dpi: int) -> None:
    """Convert between image formats."""
    if fmt == "yaml":
        raise click.ClickException(
            "Cannot convert image to YAML. Use a recipe file instead."
        )

    try:
        from PIL import Image

        img = Image.open(source)

        if fmt == "pdf":
            img.save(output, "PDF", resolution=dpi)
        elif fmt == "svg":
            raise click.ClickException(
                "Cannot convert raster image to SVG. Use a recipe file instead."
            )
        else:
            img.save(output, fmt.upper())

        click.echo(f"Converted: {output}")

    except ImportError:
        raise click.ClickException(
            "Image conversion requires Pillow. Install with: pip install figrecipe[imaging]"
        ) from None
    except Exception as e:
        raise click.ClickException(f"Conversion failed: {e}") from e

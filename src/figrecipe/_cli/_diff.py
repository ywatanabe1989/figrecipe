#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diff command - Compare images and generate hitmap visualization."""

from pathlib import Path
from typing import Optional

import click


@click.command()
@click.argument("original", type=click.Path(exists=True))
@click.argument("reproduced", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output path for hitmap image.",
)
@click.option(
    "--mode",
    type=click.Choice(["diff", "binary", "heatmap"]),
    default="diff",
    help="Visualization mode. Default: diff.",
)
@click.option(
    "--threshold",
    type=int,
    default=0,
    help="Pixel difference threshold (0-255). Default: 0 (exact match).",
)
@click.option(
    "--no-bbox",
    is_flag=True,
    help="Disable bounding boxes around diff regions.",
)
@click.option(
    "--min-region",
    type=int,
    default=10,
    help="Minimum pixel area for bounding box. Default: 10.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output statistics as JSON.",
)
def diff(
    original: str,
    reproduced: str,
    output: Optional[str],
    mode: str,
    threshold: int,
    no_bbox: bool,
    min_region: int,
    json_output: bool,
) -> None:
    """Compare two images and generate hitmap visualization.

    ORIGINAL is the path to the original image.
    REPRODUCED is the path to the reproduced image.

    The hitmap shows pixel differences:
    - diff mode: Green=match, red intensity=difference magnitude
    - binary mode: Green=match, red=mismatch
    - heatmap mode: Colormap showing difference magnitude

    Examples:
        figrecipe diff original.png reproduced.png
        figrecipe diff original.png reproduced.png -o hitmap.png --mode binary
        figrecipe diff original.png reproduced.png --threshold 5 --json
    """
    try:
        from .._utils._hitmap import create_hitmap
    except ImportError:
        raise click.ClickException(
            "Hitmap requires Pillow. Install with: pip install figrecipe[imaging]"
        ) from None

    original_path = Path(original)
    reproduced_path = Path(reproduced)

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = original_path.with_stem(f"{original_path.stem}_hitmap")

    try:
        hitmap, stats = create_hitmap(
            original_path,
            reproduced_path,
            output_path=output_path,
            mode=mode,
            threshold=threshold,
            show_bbox=not no_bbox,
            min_region_area=min_region,
        )

        if json_output:
            import json

            # Convert regions to serializable format
            output_stats = {
                "match_ratio": stats["match_ratio"],
                "mismatch_ratio": stats["mismatch_ratio"],
                "match_pixels": stats["match_pixels"],
                "mismatch_pixels": stats["mismatch_pixels"],
                "total_pixels": stats["total_pixels"],
                "max_diff": stats["max_diff"],
                "mean_diff": stats["mean_diff"],
                "mse": stats["mse"],
                "num_regions": stats["num_regions"],
                "regions": stats["regions"],
                "is_match": stats["mismatch_pixels"] == 0,
                "hitmap_path": str(output_path),
            }
            click.echo(json.dumps(output_stats, indent=2))
        else:
            # Human-readable output
            is_match = stats["mismatch_pixels"] == 0
            status = (
                click.style("MATCH", fg="green")
                if is_match
                else click.style("MISMATCH", fg="red")
            )

            click.echo(f"Comparison: {status}")
            click.echo(
                f"  Match ratio:     {stats['match_ratio']:.4f} ({stats['match_pixels']:,} pixels)"
            )
            click.echo(
                f"  Mismatch ratio:  {stats['mismatch_ratio']:.4f} ({stats['mismatch_pixels']:,} pixels)"
            )
            click.echo(f"  Max difference:  {stats['max_diff']:.1f}")
            click.echo(f"  Mean difference: {stats['mean_diff']:.4f}")
            click.echo(f"  MSE:             {stats['mse']:.4f}")
            if stats["num_regions"] > 0:
                click.echo(f"  Diff regions:    {stats['num_regions']}")
            click.echo(f"  Hitmap saved:    {output_path}")

    except Exception as e:
        raise click.ClickException(f"Comparison failed: {e}") from e

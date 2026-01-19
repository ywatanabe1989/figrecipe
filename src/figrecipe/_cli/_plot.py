#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plot command - Create figures from declarative YAML/JSON specs."""

import json
from pathlib import Path
from typing import Optional

import click


@click.command()
@click.argument("spec", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output path (default: spec_name.png).",
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
    "--style",
    type=str,
    default=None,
    help="Style preset to apply.",
)
@click.option(
    "--show",
    is_flag=True,
    help="Display the figure interactively.",
)
@click.option(
    "--save-recipe",
    is_flag=True,
    help="Also save as figrecipe YAML recipe.",
)
def plot(
    spec: str,
    output: Optional[str],
    fmt: str,
    dpi: int,
    style: Optional[str],
    show: bool,
    save_recipe: bool,
) -> None:
    """Create a figure from a declarative YAML/JSON spec.

    SPEC is a YAML or JSON file defining the plot structure.

    \b
    Example spec (YAML):
        figure:
          width_mm: 80
          height_mm: 60
        plots:
          - type: line
            x: [1, 2, 3, 4, 5]
            y: [1, 4, 9, 16, 25]
            color: blue
            label: "quadratic"
        xlabel: "X"
        ylabel: "Y"
        title: "My Plot"
    """
    from .._api._plot import create_figure_from_spec

    spec_path = Path(spec)

    # Load spec
    try:
        spec_data = _load_spec(spec_path)
    except Exception as e:
        raise click.ClickException(f"Failed to load spec: {e}") from e

    # Apply style override from CLI
    if style:
        spec_data.setdefault("figure", {})["style"] = style

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = spec_path.with_suffix(f".{fmt}")

    # Create figure
    try:
        result = create_figure_from_spec(
            spec_data,
            output_path=output_path,
            dpi=dpi,
            save_recipe=save_recipe,
            show=show,
        )
    except Exception as e:
        raise click.ClickException(f"Failed to create figure: {e}") from e

    if not show:
        click.echo(f"Saved: {result['image_path']}")
        if save_recipe and result.get("recipe_path"):
            click.echo(f"Recipe: {result['recipe_path']}")


def _load_spec(path: Path) -> dict:
    """Load YAML or JSON spec file."""
    from ruamel.yaml import YAML

    content = path.read_text()
    yaml_parser = YAML(typ="safe")

    if path.suffix.lower() in (".yaml", ".yml"):
        return yaml_parser.load(content)
    elif path.suffix.lower() == ".json":
        return json.loads(content)
    else:
        # Try YAML first, then JSON
        try:
            return yaml_parser.load(content)
        except Exception:
            return json.loads(content)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""style command - Style management subcommands."""


import click


@click.group()
def style() -> None:
    """Manage figure styles and presets."""
    pass


@style.command("list")
def list_styles() -> None:
    """List available style presets."""
    from .. import list_presets

    presets = list_presets()

    click.echo("Available style presets:")
    for preset in presets:
        click.echo(f"  - {preset}")


@style.command("show")
@click.argument("name")
def show_style(name: str) -> None:
    """Show details of a style preset.

    NAME is the preset name (e.g., SCITEX, MATPLOTLIB).
    """
    from ruamel.yaml import YAML

    from ..styles._style_loader import load_preset

    try:
        style_dict = load_preset(name)
    except Exception as e:
        raise click.ClickException(f"Failed to load preset '{name}': {e}") from e

    yaml = YAML()
    yaml.default_flow_style = False

    click.echo(f"Style preset: {name}\n")

    import io

    stream = io.StringIO()
    yaml.dump(style_dict, stream)
    click.echo(stream.getvalue())


@style.command("apply")
@click.argument("name")
def apply_style_cmd(name: str) -> None:
    """Apply a style preset globally.

    NAME is the preset name (e.g., SCITEX, MATPLOTLIB).
    """
    from .. import load_style

    try:
        load_style(name)
        click.echo(f"Applied style: {name}")
    except Exception as e:
        raise click.ClickException(f"Failed to apply style: {e}") from e


@style.command("reset")
def reset_style() -> None:
    """Reset to default matplotlib style."""
    from .. import unload_style

    unload_style()
    click.echo("Style reset to defaults.")

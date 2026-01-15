#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""style command - Style management subcommands."""

import click
from rich.console import Console

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _print_command_help(cmd, prefix: str, parent_ctx) -> None:
    """Print help for a command."""
    console.print(f"\n[bold cyan]━━━ {prefix} ━━━[/bold cyan]")
    sub_ctx = click.Context(cmd, info_name=prefix.split()[-1], parent=parent_ctx)
    console.print(cmd.get_help(sub_ctx))


def _show_recursive_help(ctx: click.Context) -> None:
    """Display recursive help for all style subcommands."""
    console.print("[bold cyan]━━━ figrecipe style ━━━[/bold cyan]")
    console.print(ctx.get_help())

    for name, cmd in sorted(style.commands.items()):
        if name == "help-recursive":
            continue
        _print_command_help(cmd, f"figrecipe style {name}", ctx)


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands.")
@click.pass_context
def style(ctx: click.Context, help_recursive: bool) -> None:
    """Manage figure styles and presets."""
    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)

    if ctx.invoked_subcommand is None and not help_recursive:
        click.echo(ctx.get_help())


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


@style.command("help-recursive", context_settings=CONTEXT_SETTINGS)
@click.pass_context
def help_recursive_cmd(ctx: click.Context) -> None:
    """Show help for all style subcommands."""
    _show_recursive_help(ctx.parent)

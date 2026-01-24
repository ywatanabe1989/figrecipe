#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CLI entry point for figrecipe."""

import click
from rich.console import Console

from .. import __version__
from ._completion import completion
from ._compose import compose
from ._convert import convert
from ._crop import crop
from ._diagram import diagram as _diagram_cmd
from ._edit import edit
from ._extract import extract
from ._fonts import fonts
from ._info import info
from ._mcp import mcp
from ._plot import plot
from ._reproduce import reproduce
from ._style import style
from ._validate import validate
from ._version import version as version_cmd

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _print_command_help(cmd, prefix: str, parent_ctx) -> None:
    """Recursively print help for a command and its subcommands."""
    console.print(f"\n[bold cyan]━━━ {prefix} ━━━[/bold cyan]")
    sub_ctx = click.Context(cmd, info_name=prefix.split()[-1], parent=parent_ctx)
    console.print(cmd.get_help(sub_ctx))

    # If this is a Group, recurse into subcommands
    if isinstance(cmd, click.Group):
        for sub_name, sub_cmd in sorted(cmd.commands.items()):
            _print_command_help(sub_cmd, f"{prefix} {sub_name}", sub_ctx)


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.option("--help-recursive", is_flag=True, help="Show help for all commands.")
@click.pass_context
def main(ctx: click.Context, version: bool, help_recursive: bool) -> None:
    """figrecipe - Reproducible matplotlib figures.

    A command-line interface for creating, reproducing, and editing
    matplotlib figures using YAML recipes.

    When run without a subcommand, launches the GUI editor.
    """
    if version:
        click.echo(f"figrecipe {__version__}")
        ctx.exit(0)

    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        ctx.invoke(edit)


def _show_recursive_help(ctx: click.Context) -> None:
    """Display recursive help for all commands."""
    console.print("[bold cyan]━━━ figrecipe ━━━[/bold cyan]")
    console.print(ctx.get_help())

    for name, cmd in sorted(main.commands.items()):
        _print_command_help(cmd, f"figrecipe {name}", ctx)


# Register commands

main.add_command(completion)
main.add_command(compose)
main.add_command(convert)
main.add_command(crop)
main.add_command(_diagram_cmd, name="diagram")
main.add_command(edit)
main.add_command(extract)
main.add_command(fonts)
main.add_command(info)
main.add_command(mcp)
main.add_command(plot)
main.add_command(reproduce)
main.add_command(style)
main.add_command(validate)
main.add_command(version_cmd)


if __name__ == "__main__":
    main()

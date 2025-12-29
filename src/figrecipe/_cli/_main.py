#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CLI entry point for figrecipe."""


import click

from .. import __version__


@click.group(invoke_without_command=True)
@click.option("--version", "-V", is_flag=True, help="Show version and exit.")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """figrecipe - Reproducible matplotlib figures.

    A command-line interface for creating, reproducing, and editing
    matplotlib figures using YAML recipes.
    """
    if version:
        click.echo(f"figrecipe {__version__}")
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Import and register commands
from ._compose import compose
from ._convert import convert
from ._crop import crop
from ._edit import edit
from ._extract import extract
from ._fonts import fonts
from ._info import info
from ._reproduce import reproduce
from ._style import style
from ._validate import validate
from ._version import version

main.add_command(reproduce)
main.add_command(info)
main.add_command(extract)
main.add_command(validate)
main.add_command(edit)
main.add_command(crop)
main.add_command(compose)
main.add_command(style)
main.add_command(convert)
main.add_command(fonts)
main.add_command(version)


if __name__ == "__main__":
    main()

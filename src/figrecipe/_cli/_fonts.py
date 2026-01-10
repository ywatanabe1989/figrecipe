#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fonts command - Font management."""

from typing import Optional

import click


@click.command()
@click.option(
    "--check",
    type=str,
    help="Check if a specific font is available.",
)
@click.option(
    "--search",
    type=str,
    help="Search for fonts matching a pattern.",
)
def fonts(check: Optional[str], search: Optional[str]) -> None:
    """List or check available fonts."""
    from ..styles._style_applier import check_font, list_available_fonts

    if check:
        available = check_font(check)
        if available:
            click.echo(f"Font '{check}' is available.")
        else:
            click.echo(f"Font '{check}' is NOT available.")
            raise SystemExit(1)
        return

    all_fonts = list_available_fonts()

    if search:
        pattern = search.lower()
        matching = [f for f in all_fonts if pattern in f.lower()]
        click.echo(f"Fonts matching '{search}':")
        for font in sorted(matching):
            click.echo(f"  {font}")
        click.echo(f"\nFound {len(matching)} matching fonts.")
    else:
        click.echo("Available fonts:")
        for font in sorted(all_fonts):
            click.echo(f"  {font}")
        click.echo(f"\nTotal: {len(all_fonts)} fonts.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""version command - Show version information."""

import click


@click.command()
@click.option(
    "--full",
    is_flag=True,
    help="Show full version info with dependencies.",
)
def version(full: bool) -> None:
    """Show version information."""
    from .. import __version__

    click.echo(f"figrecipe {__version__}")

    if full:
        click.echo()
        _show_dependency_versions()


def _show_dependency_versions() -> None:
    """Show versions of key dependencies."""
    deps = [
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy"),
        ("ruamel.yaml", "ruamel.yaml"),
        ("scipy", "scipy"),
        ("Pillow", "PIL"),
        ("seaborn", "seaborn"),
        ("pandas", "pandas"),
        ("flask", "flask"),
    ]

    click.echo("Dependencies:")
    for name, module in deps:
        try:
            mod = __import__(module)
            ver = getattr(mod, "__version__", "unknown")
            click.echo(f"  {name}: {ver}")
        except ImportError:
            click.echo(f"  {name}: not installed")

    # Python version
    import sys

    click.echo(f"\nPython: {sys.version}")

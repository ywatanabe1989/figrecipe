#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""edit command - Launch GUI editor."""

from pathlib import Path
from typing import Optional

import click


@click.command()
@click.argument("source", type=click.Path(exists=True), required=False)
@click.option(
    "--port",
    type=int,
    default=5050,
    help="Server port (default: 5050).",
)
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Host to bind (default: 127.0.0.1).",
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Don't auto-open browser.",
)
@click.option(
    "--desktop",
    is_flag=True,
    help="Launch as native desktop window (requires pywebview).",
)
def edit(
    source: Optional[str],
    port: int,
    host: str,
    no_browser: bool,
    desktop: bool,
) -> None:
    """Launch interactive GUI editor.

    SOURCE is the optional path to a .yaml recipe file or bundle.
    If not provided, creates a new blank figure.
    """
    try:
        from .. import edit as fr_edit
    except ImportError:
        raise click.ClickException(
            "Editor requires Flask. Install with: pip install figrecipe[editor]"
        ) from None

    source_path = Path(source) if source else None

    if desktop:
        click.echo("Starting editor in desktop mode...")
    else:
        click.echo(f"Starting editor on http://{host}:{port}")

    try:
        fr_edit(
            source_path,
            port=port,
            host=host,
            open_browser=not no_browser,
            desktop=desktop,
        )
    except Exception as e:
        raise click.ClickException(f"Editor failed: {e}") from e

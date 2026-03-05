#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gui command - Launch GUI editor."""

from pathlib import Path
from typing import Optional

import click


def _kill_port(port: int) -> bool:
    """Kill process occupying the given port. Returns True if killed."""
    import subprocess

    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
        )
        pids = result.stdout.strip().split()
        if not pids:
            return False
        for pid in pids:
            subprocess.run(["kill", "-9", pid], capture_output=True)
        return True
    except FileNotFoundError:
        # lsof not available, try fuser
        try:
            subprocess.run(
                ["fuser", "-k", f"{port}/tcp"],
                capture_output=True,
            )
            return True
        except FileNotFoundError:
            return False


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
@click.option(
    "--force",
    is_flag=True,
    help="Kill existing process on port before starting.",
)
def gui(
    source: Optional[str],
    port: int,
    host: str,
    no_browser: bool,
    desktop: bool,
    force: bool,
) -> None:
    """Launch interactive GUI editor.

    SOURCE is the optional path to a .yaml recipe file or bundle.
    If not provided, creates a new blank figure.
    """
    from .. import gui as fr_gui

    if force:
        if _kill_port(port):
            import time

            click.echo(f"Killed existing process on port {port}")
            time.sleep(0.5)  # Brief wait for port release

    source_path = Path(source) if source else None
    working_dir = None

    # If source is a directory without recipe.yaml, use it as working_dir
    if source_path is not None and source_path.is_dir():
        recipe_yaml = source_path / "recipe.yaml"
        if not recipe_yaml.exists():
            working_dir = source_path
            source_path = None
            click.echo(f"Browsing directory: {working_dir}")

    if desktop:
        click.echo("Starting editor in desktop mode...")
    else:
        click.echo(f"Starting editor on http://{host}:{port}")

    try:
        fr_gui(
            source_path,
            port=port,
            host=host,
            open_browser=not no_browser,
            desktop=desktop,
            working_dir=working_dir,
        )
    except Exception as e:
        raise click.ClickException(f"Editor failed: {e}") from e

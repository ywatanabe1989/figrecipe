#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP server commands for figrecipe."""

import click


@click.group()
def mcp():
    """MCP (Model Context Protocol) server commands."""
    pass


@mcp.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to.")
@click.option("--port", default=8000, type=int, help="Port to bind to.")
def run(host: str, port: int) -> None:
    """Run the figrecipe MCP server.

    The server provides tools for creating matplotlib figures from
    declarative specifications.
    """
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"Failed to import MCP server. Install fastmcp: pip install fastmcp\n{e}"
        ) from e

    click.echo(f"Starting figrecipe MCP server on {host}:{port}")
    mcp_server.run()


@mcp.command()
def info() -> None:
    """Show MCP server information and available tools."""
    try:
        import fastmcp  # noqa: F401
    except ImportError as e:
        raise click.ClickException(
            f"fastmcp not installed. Install with: pip install fastmcp\n{e}"
        ) from e

    click.echo("figrecipe MCP Server")
    click.echo("=" * 40)
    click.echo()
    click.echo("Available tools:")
    for tool_name in [
        "plot",
        "reproduce",
        "compose",
        "info",
        "validate",
        "crop",
        "extract_data",
        "list_styles",
        "get_plot_types",
    ]:
        click.echo(f"  - {tool_name}")
    click.echo()
    click.echo("Usage:")
    click.echo("  figrecipe mcp run")
    click.echo("  fastmcp run figrecipe._mcp.server:mcp")

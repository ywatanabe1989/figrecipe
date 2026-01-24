#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP server commands for figrecipe."""

import click


@click.group()
def mcp():
    """MCP (Model Context Protocol) server commands."""
    pass


@mcp.command("run")
@click.option("--host", default="127.0.0.1", help="Host to bind to.")
@click.option("--port", default=8000, type=int, help="Port to bind to.")
def run_server(host: str, port: int) -> None:
    """Run the figrecipe MCP server."""
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"Failed to import MCP server. Install fastmcp: pip install fastmcp\n{e}"
        ) from e

    click.echo(f"Starting figrecipe MCP server on {host}:{port}")
    mcp_server.run()


@mcp.command("list-tools")
def list_tools() -> None:
    """List available MCP tools."""
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"fastmcp not installed. Install with: pip install figrecipe[mcp]\n{e}"
        ) from e

    click.echo("Available MCP tools:")
    for tool in mcp_server._tool_manager._tools.values():
        click.echo(f"  - {tool.name}")


@mcp.command("doctor")
def doctor() -> None:
    """Check MCP server dependencies and configuration."""
    click.echo("Checking MCP dependencies...")

    # Check fastmcp
    try:
        import fastmcp

        click.echo(f"  ✓ fastmcp {fastmcp.__version__}")
    except ImportError:
        click.echo("  ✗ fastmcp not installed")
        click.echo("    Install with: pip install figrecipe[mcp]")
        return

    # Check server imports
    try:
        from .._mcp.server import mcp as mcp_server

        click.echo(
            f"  ✓ MCP server loaded ({len(mcp_server._tool_manager._tools)} tools)"
        )
    except Exception as e:
        click.echo(f"  ✗ MCP server error: {e}")
        return

    click.echo("\nMCP server is ready.")
    click.echo("Run with: figrecipe mcp run")


@mcp.command("install")
@click.option("--claude-code", is_flag=True, help="Show Claude Code config.")
def install(claude_code: bool) -> None:
    """Show MCP server installation instructions."""
    if claude_code:
        click.echo("Add to your Claude Code MCP config:")
        click.echo()
        click.echo('  "figrecipe": {')
        click.echo('    "command": "figrecipe",')
        click.echo('    "args": ["mcp", "run"]')
        click.echo("  }")
    else:
        click.echo("figrecipe MCP Server Installation")
        click.echo("=" * 40)
        click.echo()
        click.echo("1. Install MCP dependencies:")
        click.echo("   pip install figrecipe[mcp]")
        click.echo()
        click.echo("2. For Claude Code, add to MCP config:")
        click.echo("   figrecipe mcp install --claude-code")
        click.echo()
        click.echo("3. Test the server:")
        click.echo("   figrecipe mcp doctor")


@mcp.command("info")
def info() -> None:
    """Show MCP server information."""
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"fastmcp not installed. Install with: pip install figrecipe[mcp]\n{e}"
        ) from e

    click.echo("figrecipe MCP Server")
    click.echo("=" * 40)
    click.echo()
    click.echo("Available tools:")
    for tool in mcp_server._tool_manager._tools.values():
        click.echo(f"  - {tool.name}")
    click.echo()
    click.echo("Usage:")
    click.echo("  figrecipe mcp run")
    click.echo("  fastmcp run figrecipe._mcp.server:mcp")

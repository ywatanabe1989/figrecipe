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


def _format_signature(tool) -> str:
    """Format tool as Python-like function signature."""
    params = []
    if hasattr(tool, "parameters") and tool.parameters:
        schema = tool.parameters
        props = schema.get("properties", {})
        required = schema.get("required", [])
        for name, info in props.items():
            ptype = info.get("type", "any")
            default = info.get("default")
            if name in required:
                params.append(f"{name}: {ptype}")
            elif default is not None:
                params.append(f"{name}: {ptype} = {default!r}")
            else:
                params.append(f"{name}: {ptype} = None")
    return f"{tool.name}({', '.join(params)})"


def _estimate_tokens(text: str) -> int:
    """Estimate token count (rough: ~4 chars per token)."""
    return len(text) // 4 if text else 0


def _get_mcp_summary(mcp_server) -> dict:
    """Get MCP server summary statistics."""
    import json as json_mod

    tools = list(mcp_server._tool_manager._tools.values())
    instructions = getattr(mcp_server, "instructions", "") or ""
    total_desc = sum(len(t.description or "") for t in tools)
    total_params = sum(
        len(json_mod.dumps(t.parameters))
        if hasattr(t, "parameters") and t.parameters
        else 0
        for t in tools
    )

    return {
        "name": getattr(mcp_server, "name", "unknown"),
        "tool_count": len(tools),
        "instructions_tokens": _estimate_tokens(instructions),
        "descriptions_tokens": _estimate_tokens("x" * total_desc),
        "schemas_tokens": _estimate_tokens("x" * total_params),
        "total_context_tokens": (
            _estimate_tokens(instructions)
            + _estimate_tokens("x" * total_desc)
            + _estimate_tokens("x" * total_params)
        ),
    }


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v, -vv, -vvv.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option("--summary", "show_summary", is_flag=True, help="Show context summary.")
def list_tools(verbose: int, as_json: bool, show_summary: bool) -> None:
    """List available MCP tools.

    Verbosity: (none) names, -v signatures, -vv +description, -vvv full.
    """
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"fastmcp not installed. Install with: pip install figrecipe[mcp]\n{e}"
        ) from e

    tools = list(mcp_server._tool_manager._tools.values())
    summary = _get_mcp_summary(mcp_server)

    if as_json:
        import json

        tool_data = []
        for tool in tools:
            schema = tool.parameters if hasattr(tool, "parameters") else {}
            tool_data.append(
                {
                    "name": tool.name,
                    "signature": _format_signature(tool),
                    "description": tool.description,
                    "parameters": schema,
                }
            )
        output = {"summary": summary, "tools": tool_data}
        click.echo(json.dumps(output, indent=2))
        return

    # Header with summary
    click.echo(f"MCP Server: {summary['name']}")
    click.echo(f"Tools: {summary['tool_count']}")
    if show_summary:
        click.echo(f"Context: ~{summary['total_context_tokens']:,} tokens")
        click.echo(f"  Instructions: ~{summary['instructions_tokens']:,} tokens")
        click.echo(f"  Descriptions: ~{summary['descriptions_tokens']:,} tokens")
        click.echo(f"  Schemas: ~{summary['schemas_tokens']:,} tokens")
    click.echo()

    for tool in tools:
        if verbose == 0:
            click.echo(f"  {tool.name}")
        elif verbose == 1:
            click.echo(f"  {_format_signature(tool)}")
        elif verbose == 2:
            click.echo(f"  {_format_signature(tool)}")
            if tool.description:
                desc = tool.description.split("\n")[0].strip()
                click.echo(f"    {desc}")
            click.echo()
        else:
            click.echo(f"  {_format_signature(tool)}")
            if tool.description:
                for line in tool.description.strip().split("\n"):
                    click.echo(f"    {line}")
            click.echo()


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

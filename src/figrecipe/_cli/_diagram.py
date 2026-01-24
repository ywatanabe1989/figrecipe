#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands for diagram creation and manipulation."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.syntax import Syntax

console = Console()


@click.group()
def diagram():
    """Create and manage diagrams (flowcharts, pipelines, etc.)."""
    pass


@diagram.command("create")
@click.argument("output", type=click.Path())
@click.option(
    "--type",
    "-t",
    "diagram_type",
    type=click.Choice(["workflow", "decision", "pipeline", "hierarchy"]),
    default="workflow",
    help="Diagram type (default: workflow)",
)
@click.option("--title", help="Diagram title")
@click.option("--column", type=click.Choice(["single", "double"]), default="single")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["mermaid", "graphviz", "yaml"]),
    default="mermaid",
    help="Output format (default: mermaid)",
)
def create(
    output: str,
    diagram_type: str,
    title: Optional[str],
    column: str,
    output_format: str,
):
    """Create a new diagram from command line.

    Example:
        figrecipe diagram create workflow.mmd --type pipeline --title "Data Pipeline"
    """
    from .._diagram import Diagram

    d = Diagram(type=diagram_type, title=title or "", column=column)
    output_path = Path(output)

    if output_format == "mermaid":
        content = d.to_mermaid(output_path)
    elif output_format == "graphviz":
        content = d.to_graphviz(output_path)
    else:
        content = d.to_yaml(output_path)

    console.print(f"[green]✓[/green] Created diagram: {output_path}")
    console.print(Syntax(content, "text" if output_format == "yaml" else output_format))


@diagram.command("convert")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["mermaid", "graphviz", "yaml"]),
    help="Output format (auto-detected from extension if not specified)",
)
def convert(input: str, output: str, output_format: Optional[str]):
    """Convert diagram between formats.

    Example:
        figrecipe diagram convert workflow.yaml workflow.mmd
        figrecipe diagram convert workflow.mmd workflow.dot -f graphviz
    """
    from .._diagram import Diagram

    input_path = Path(input)
    output_path = Path(output)

    # Load diagram
    if input_path.suffix in (".yaml", ".yml"):
        d = Diagram.from_yaml(input_path)
    elif input_path.suffix == ".mmd":
        d = Diagram.from_mermaid(input_path)
    else:
        console.print(f"[red]Error:[/red] Unknown input format: {input_path.suffix}")
        raise SystemExit(1)

    # Detect output format
    if output_format is None:
        if output_path.suffix == ".mmd":
            output_format = "mermaid"
        elif output_path.suffix in (".dot", ".gv"):
            output_format = "graphviz"
        elif output_path.suffix in (".yaml", ".yml"):
            output_format = "yaml"
        else:
            output_format = "mermaid"

    # Save
    if output_format == "mermaid":
        d.to_mermaid(output_path)
    elif output_format == "graphviz":
        d.to_graphviz(output_path)
    else:
        d.to_yaml(output_path)

    console.print(f"[green]✓[/green] Converted: {input_path} → {output_path}")


@diagram.command("info")
@click.argument("path", type=click.Path(exists=True))
def info(path: str):
    """Show information about a diagram file.

    Example:
        figrecipe diagram info workflow.yaml
    """
    from .._diagram import Diagram

    input_path = Path(path)

    # Load diagram
    if input_path.suffix in (".yaml", ".yml"):
        d = Diagram.from_yaml(input_path)
    elif input_path.suffix == ".mmd":
        d = Diagram.from_mermaid(input_path)
    else:
        console.print(f"[red]Error:[/red] Unknown format: {input_path.suffix}")
        raise SystemExit(1)

    console.print(f"[bold]Diagram Info:[/bold] {input_path}")
    console.print(f"  Type: {d.spec.type.value}")
    console.print(f"  Title: {d.spec.title or '(none)'}")
    console.print(f"  Nodes: {len(d.spec.nodes)}")
    console.print(f"  Edges: {len(d.spec.edges)}")
    console.print(f"  Groups: {len(d.spec.layout.groups)}")
    console.print(
        f"  Column: {d.spec.paper.column.value if hasattr(d.spec.paper.column, 'value') else d.spec.paper.column}"
    )


@diagram.command("presets")
def presets():
    """List available diagram presets."""
    from .._diagram import list_presets as list_diagram_presets

    preset_info = list_diagram_presets()

    console.print("[bold]Available Diagram Presets:[/bold]")
    for name, desc in preset_info.items():
        console.print(f"  [cyan]{name}[/cyan]: {desc}")


@diagram.command("split")
@click.argument("input", type=click.Path(exists=True))
@click.option("--max-nodes", "-n", default=12, help="Max nodes per split (default: 12)")
@click.option(
    "--strategy",
    "-s",
    type=click.Choice(["by_groups", "by_articulation"]),
    default="by_groups",
    help="Split strategy",
)
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory")
def split(input: str, max_nodes: int, strategy: str, output_dir: Optional[str]):
    """Split a large diagram into multiple parts.

    Example:
        figrecipe diagram split large_workflow.yaml --max-nodes 8 -o parts/
    """
    from .._diagram import Diagram

    input_path = Path(input)

    if input_path.suffix in (".yaml", ".yml"):
        d = Diagram.from_yaml(input_path)
    else:
        console.print("[red]Error:[/red] Split only supports YAML input")
        raise SystemExit(1)

    parts = d.split(max_nodes=max_nodes, strategy=strategy)

    if len(parts) == 1:
        console.print("[yellow]Note:[/yellow] Diagram doesn't need splitting")
        return

    out_dir = Path(output_dir) if output_dir else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, part in enumerate(parts):
        out_name = f"{input_path.stem}_part{i + 1}.mmd"
        out_path = out_dir / out_name
        part.to_mermaid(out_path)
        console.print(
            f"[green]✓[/green] Created: {out_path} ({len(part.spec.nodes)} nodes)"
        )

    console.print(f"\n[bold]Split into {len(parts)} parts[/bold]")


@diagram.command("render")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "svg", "pdf"]),
    help="Output format (auto-detected from extension)",
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["auto", "mermaid-cli", "graphviz", "mermaid.ink"]),
    default="auto",
    help="Rendering backend",
)
@click.option("--scale", "-s", default=2.0, help="Scale factor (default: 2.0)")
def render(
    input: str,
    output: str,
    format: Optional[str],
    backend: str,
    scale: float,
):
    """Render diagram to image (PNG, SVG, PDF).

    Example:
        figrecipe diagram render workflow.yaml workflow.png
        figrecipe diagram render workflow.mmd output.svg --backend mermaid.ink
    """
    from .._diagram import Diagram

    input_path = Path(input)
    output_path = Path(output)

    # Auto-detect format from extension
    if format is None:
        format = output_path.suffix.lstrip(".").lower()
        if format not in ("png", "svg", "pdf"):
            format = "png"

    # Load diagram
    if input_path.suffix in (".yaml", ".yml"):
        d = Diagram.from_yaml(input_path)
    elif input_path.suffix == ".mmd":
        d = Diagram.from_mermaid(input_path)
    else:
        console.print(f"[red]Error:[/red] Unknown input format: {input_path.suffix}")
        raise SystemExit(1)

    try:
        result = d.render(output_path, format=format, backend=backend, scale=scale)
        console.print(f"[green]✓[/green] Rendered: {result}")
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@diagram.command("backends")
def backends():
    """Show available rendering backends and their status."""
    from .._diagram._render import get_available_backends

    backend_info = get_available_backends()

    console.print("[bold]Diagram Rendering Backends:[/bold]")
    for name, info in backend_info.items():
        status = "[green]✓[/green]" if info["available"] else "[red]✗[/red]"
        console.print(f"  {status} {name}")
        console.print(f"      Formats: {', '.join(info['formats'])}")
        if not info["available"]:
            console.print(f"      Install: {info['install']}")

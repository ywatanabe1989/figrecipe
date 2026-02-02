# FigRecipe Examples

Demonstration scripts showcasing FigRecipe's capabilities for reproducible scientific figures.

## Quick Start

```bash
# Run all examples
./00_run_all.sh

# Run specific examples
./00_run_all.sh 01 02 03

# Clean output directories
./00_run_all.sh --clean

# List available examples
./00_run_all.sh --list
```

## Examples Overview

| # | File | Description |
|---|------|-------------|
| 01 | `01_plot_and_reproduce_all.py` | Generate & reproduce all 47 plot types |
| 02 | `02_compose_and_reproduce.py` | Multi-panel figure composition |
| 03 | `03_statistical_notations_and_captions.py` | Statistical annotations & captions |
| 04 | `04_style_scitex_anatomy.py` | SCITEX style anatomy diagram |
| 05 | `05_style_change.py` | Style switching demonstration |
| 06 | `06_gui_editor.py` | GUI editor (requires interaction) |
| 07 | `07_diagram.py` | Mermaid/Graphviz diagram generation |
| 08 | `08_figrecipe_workflow.py` | End-to-end workflow demo |
| 09 | `09_cli_commands.sh` | CLI commands demonstration |
| 10 | `10_mcp.sh` / `10_mcp.py` | MCP (Model Context Protocol) integration |
| 11 | `11_check_api.py` | API cleanliness verification |

## Example Details

### 01. Plot and Reproduce All
Generates all 47 supported plot types and validates pixel-perfect reproduction from YAML recipes.

### 02. Composition
Demonstrates multi-panel figure composition with:
- Grid-based layout (horizontal, vertical, grid)
- Free-form mm-based positioning
- Automatic panel labels (A, B, C...)

### 03. Statistical Notations and Captions
Shows statistical annotation features:
- Significance brackets with stars (*, **, ***)
- P-value display formats
- Automatic caption generation from stats metadata

### 04. SCITEX Style Anatomy
Visual anatomy of the SCITEX publication-ready style showing all configurable parameters.

### 05. Style Change
Demonstrates runtime style switching between presets (SCITEX, matplotlib defaults, custom).

### 06. GUI Editor
Interactive Flask-based editor for visual figure editing. Run manually:
```bash
python 06_gui_editor.py
```

### 07. Diagram
Scientific diagram generation using:
- Mermaid syntax
- Graphviz DOT format
- YAML specifications

### 08. FigRecipe Workflow
Complete end-to-end demonstration of the FigRecipe workflow from data to publication.

### 09. CLI Commands
Shell script demonstrating CLI tools:
```bash
figrecipe info recipe.yaml
figrecipe reproduce recipe.yaml
figrecipe crop figure.png
```

### 10. MCP Integration
Model Context Protocol integration for AI agents (Claude Code):
- `10_mcp.sh`: CLI-based demo
- `10_mcp.py`: Python-based declarative specification demo

### 11. API Check
Verifies that the public API is clean and exports only intended symbols.

## Output Directories

Each example creates an `*_out/` directory with generated figures:
```
examples/
├── 01_plot_and_reproduce_all_out/
├── 02_compose_and_reproduce_out/
├── 03_statistical_notations_and_captions_out/
├── 04_style_scitex_anatomy_out/
├── 05_style_change_out/
├── 07_diagram_out/
├── 08_figrecipe_workflow_out/
├── 10_mcp_out/
└── 11_check_api_out/
```

## Requirements

- Python 3.10+
- FigRecipe installed: `pip install -e .`
- Virtual environment activated: `source .venv/bin/activate`

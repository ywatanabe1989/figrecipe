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

### Recommended Starting Point

**01. Bundle Format** (`01_bundle_format.py`) - The recommended way to save and share figures:
```python
import figrecipe as fr

fig, ax = fr.subplots()
ax.scatter(x, y, id="data")

# Save as self-contained ZIP bundle
fr.save(fig, "figure.zip")

# Load and reproduce
spec, style, data = fr.load_bundle("figure.zip")
fig2, ax2 = fr.reproduce_bundle("figure.zip")
```

The ZIP bundle packages everything needed for reproducibility:
- `spec.json` - WHAT to plot (semantic specification)
- `style.json` - HOW it looks (colors, fonts, sizes)
- `data.csv` - Immutable source data
- `exports/` - PNG and hitmap images

### All Examples

| # | File | Description |
|---|------|-------------|
| 01 | `01_bundle_format.py` | **ZIP bundle format (recommended for sharing)** |
| 02 | `02_plot_and_reproduce_all.py` | Generate & reproduce all 47 plot types |
| 03 | `03_compose_and_reproduce.py` | Multi-panel figure composition |
| 03a | `03a_composition.py` | Simple composition |
| 03b | `03b_composition_mm.py` | mm-based positioning |
| 04 | `04_statistical_notations.py` | Statistical annotations & captions |
| 05a | `05a_style_anatomy.py` | Style anatomy diagram |
| 05b | `05b_style_scitex_anatomy.py` | SCITEX style anatomy |
| 06 | `06_style_change.py` | Style switching demonstration |
| 07 | `07_csv_workflow.py` | CSV workflow demonstration |
| 08 | `08_diagram.py` | Scientific diagrams (native matplotlib) |
| 09 | `09_gui_editor.py` | GUI editor (interactive) |
| 10 | `10_figrecipe_workflow.py` | End-to-end workflow demo |
| 11 | `11_infographic.py` | Infographic creation (WIP) |
| 12 | `12_mcp.py` | MCP (Model Context Protocol) integration |
| 13 | `13_check_api.py` | API cleanliness verification |

## Example Details

### 01. Bundle Format (Recommended)
The recommended way to create and share reproducible figures:
- Saves as self-contained ZIP bundle
- Includes spec.json, style.json, data.csv
- Preserves hitmap for GUI editing

### 02. Plot and Reproduce All
Generates all 47 supported plot types and validates pixel-perfect reproduction from YAML recipes.

### 03. Composition
Demonstrates multi-panel figure composition with:
- Grid-based layout (horizontal, vertical, grid)
- Free-form mm-based positioning
- Automatic panel labels (A, B, C...)

### 04. Statistical Notations
Shows statistical annotation features:
- Significance brackets with stars (*, **, ***)
- P-value display formats
- Automatic caption generation from stats metadata

### 05. Style Anatomy
Visual anatomy of style systems showing all configurable parameters.

### 06. Style Change
Demonstrates runtime style switching between presets (SCITEX, matplotlib defaults, custom).

### 07. CSV Workflow
Creating figures from CSV data files.

### 08. Diagram
Scientific diagram generation using native matplotlib rendering.

### 09. GUI Editor
Interactive Flask-based editor for visual figure editing. Run manually:
```bash
python 09_gui_editor.py
```

### 10. FigRecipe Workflow
Complete end-to-end demonstration of the FigRecipe workflow from data to publication.

### 12. MCP Integration
Model Context Protocol integration for AI agents (Claude Code).

### 13. API Check
Verifies that the public API is clean and exports only intended symbols.

## Output Directories

Each example creates an `*_out/` directory with generated figures:
```
examples/
├── 01_bundle_format_out/
├── 02_plot_and_reproduce_all_out/
├── 03_compose_and_reproduce_out/
├── 04_statistical_notations_out/
├── 05a_style_anatomy_out/
├── 08_diagram_out/
├── 10_figrecipe_workflow_out/
├── 12_mcp_out/
└── 13_check_api_out/
```

## Requirements

- Python 3.10+
- FigRecipe installed: `pip install -e .`
- Virtual environment activated: `source .venv/bin/activate`

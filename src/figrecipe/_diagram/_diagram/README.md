<!-- ---
!-- Timestamp: 2026-02-15 01:00:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_diagram/_diagram/README.md
!-- --- -->

# Diagram Module

Publication-quality box-and-arrow diagrams with programmatic layout validation.

## Quick Start

```python
import figrecipe as fr

s = fr.Diagram(width_mm=170, height_mm=120)
s.add_box("a", "Input", x_mm=30, y_mm=60, width_mm=40, height_mm=25)
s.add_box("b", "Output", x_mm=130, y_mm=60, width_mm=40, height_mm=25)
s.add_arrow("a", "b", label="process")
s.render_to_file("diagram.png")
```

## Validation Rules

All rules are enforced automatically on `render()`. Errors are **collected and
reported together** so you see the full picture before fixing.

| Rule | Check | Severity |
|------|-------|----------|
| R1 | Container must enclose all children | ValueError |
| R2 | No two boxes may overlap | ValueError |
| R3 | Container title must clear children (5mm zone) | UserWarning |
| R4 | Box text must fit within padded inner area | UserWarning |
| R5 | Text-to-text margin >= 2mm | ValueError |
| R6 | Text-to-edge margin >= 2mm | ValueError |
| R7 | Arrow visible-length ratio >= 90% | ValueError |
| R8 | Curved-arrow label on same side as arc | ValueError |

### Thresholds (centralised in `_validate.py`)

```python
MIN_MARGIN_MM = 2.0  # R5, R6
MIN_VISIBLE = 0.9    # R7
```

### Error Output Example

```
ValueError: 2 validation error(s):
  R5/R6: Text margin violation: 'reproduce' and 'validate' gap=1.1mm (min=2.0mm)
  R7: 'arrow:figure->recipe' visibility 28% < 90%. Occluded by: 'reproduce'
```

### Failed Figure Output

When validation fails, `render_to_file()` still saves the figure with a
`_FAILED` suffix so you can inspect what went wrong:

```
diagram_FAILED.png   # errored figure for inspection
```

## Shapes

| Shape | Description | Visual |
|-------|-------------|--------|
| `rounded` | Rounded rectangle (default) | General-purpose nodes |
| `box` | Sharp-cornered rectangle | Structural elements |
| `stadium` | Pill-shaped (highly rounded) | Status/badge nodes |
| `cylinder` | Database cylinder | Data stores, files |
| `document` | Paper with folded corner | Reports, manuscripts |
| `file` | Folder with tab | Directories, file groups |
| `codeblock` | Terminal window with title bar | Scripts, code snippets |

### Semantic Node Classes

Use `node_class` to auto-select shapes:

```python
s.add_box("script", "run_analysis.py", node_class="code")       # -> codeblock
s.add_box("data", "results.csv", node_class="input")            # -> cylinder
s.add_box("report", "Figure 1", node_class="claim")             # -> document
```

| Class | Default Shape | Meaning |
|-------|---------------|---------|
| `source` | rounded | Acquisition scripts |
| `input` | cylinder | Raw data, configuration |
| `processing` | rounded | Transform/analysis |
| `output` | cylinder | Intermediate/final data |
| `claim` | document | Paper assertions |
| `code` | codeblock | Scripts, commands |

## Element IDs

Every element has an ID for precise error reporting:

- **Boxes**: user-defined (`"python"`, `"recipe"`, ...)
- **Containers**: user-defined (`"concerns"`, `"benefits"`, ...)
- **Arrows**: auto-generated as `"arrow:source->target"`

## Examples

| File | Purpose |
|------|---------|
| `09b_diagram_NG_patterns.py` | Triggers each rule -- NG pattern reference |
| `10a_figrecipe_concept_diagram_error.py` | Intentionally failing layout |
| `10b_figrecipe_concept_diagram_fixed.py` | Corrected layout passing all rules |

## Architecture

```
_diagram/_diagram/
  __init__.py          # Exports: Diagram
  _core.py             # Builder, render, ArrowSpec, BoxSpec
  _validate.py         # All validation rules (R1-R8)
  _layout.py           # auto_layout() algorithms
  _io.py               # to_dict / from_dict serialization
  _editor.py           # GUI editing support
  _autofix.py          # Auto-fix validation failures
  _overlap.py          # Overlap resolution logic
  _flex.py             # CSS flexbox-like layout
  _render.py           # Matplotlib rendering
  _geom.py             # Geometry helpers
  _icons.py            # Icon support
  _codeblock.py        # Codeblock shape renderer
  _constants.py        # Shared constants
  README.md            # This file
```

<!-- EOF -->

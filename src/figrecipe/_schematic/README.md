<!-- ---
!-- Timestamp: 2026-02-07 18:37:02
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_schematic/README.md
!-- --- -->

# Schematic Module

Publication-quality box-and-arrow diagrams with programmatic layout validation.

## Quick Start

```python
import figrecipe as fr

s = fr.Schematic(width_mm=170, height_mm=120)
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

### Thresholds (centralised in `_schematic_validate.py`)

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

## Element IDs

Every element has an ID for precise error reporting:

- **Boxes**: user-defined (`"python"`, `"recipe"`, ...)
- **Containers**: user-defined (`"concerns"`, `"benefits"`, ...)
- **Arrows**: auto-generated as `"arrow:source->target"`

## Examples

| File | Purpose |
|------|---------|
| `09b_schematic_NG_patterns.py` | Triggers each rule -- NG pattern reference |
| `10a_figrecipe_concept_schematic_error.py` | Intentionally failing layout |
| `10b_figrecipe_concept_schematic_fixed.py` | Corrected layout passing all rules |

## Architecture

```
_schematic/
  __init__.py              # Exports: Schematic
  _schematic.py            # Builder, render, ArrowSpec, BoxSpec
  _schematic_validate.py   # All validation rules (R1-R8)
  _schematic_layout.py     # auto_layout() algorithms
  _schematic_io.py         # to_dict / from_dict serialization
  _schematic_editor.py     # GUI editing support
  README.md                # This file
```

<!-- EOF -->

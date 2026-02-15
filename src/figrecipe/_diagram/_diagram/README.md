<!-- ---
!-- Timestamp: 2026-02-15 01:00:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_diagram/_diagram/README.md
!-- --- -->

# Diagram Module

Publication-quality box-and-arrow diagrams with mm-based coordinates, automatic layout, and validation.

## Quick Start

```python
from figrecipe._diagram import Diagram

d = Diagram(title="My Pipeline", gap_mm=10)
d.add_box("a", "Input", shape="cylinder")
d.add_box("b", "Process", emphasis="primary")
d.add_box("c", "Output", shape="document")
d.add_arrow("a", "b")
d.add_arrow("b", "c")
d.save("pipeline.png")
# Output: pipeline.png, pipeline.yaml, pipeline_hitmap.png, pipeline_debug.png
```

## API

### Diagram(title, width_mm, height_mm, gap_mm)

- `gap_mm`: Enables flex layout mode (auto-positions elements, no manual x/y needed)
- `width_mm`: Canvas width (default: 170mm, warns if > 185mm)

### d.add_box(id, title, ...)

Key parameters: `subtitle`, `content` (list), `emphasis`, `shape`, `fill_color`, `border_color`, `padding_mm`, `bullet` ("circle"/"dash"/"arrow"), `node_class`, `state`.

### d.add_container(id, children, ...)

Groups boxes. Key parameters: `title`, `direction` ("row"/"column"), `emphasis`, `fill_color`, `border_color`, `title_loc`.

### d.add_arrow(source, target, ...)

Key parameters: `source_anchor`, `target_anchor`, `label`, `style` ("solid"/"dashed"), `color`, `curve`, `linewidth_mm`, `label_offset_mm`.

### d.render(auto_fix, auto_curve) -> (fig, ax)

- `auto_fix=True`: Resolves layout violations automatically (R1, R2, R5-R9)
- `auto_curve=True`: Auto-curves bidirectional arrows (R7)

### d.save(path, dpi, watermark) -> Path

Renders, auto-crops, and saves. Also generates recipe YAML, hitmap, and debug image.
- `watermark=True`: Stamps "Plotted by FigRecipe" (7pt, alpha=0.85)

## Validation Rules

All rules are enforced on `render()`. Failed figures save with `_FAILED` suffix.

| Rule | Check | Severity |
|------|-------|----------|
| R1 | Container must enclose all children | Error |
| R2 | No two boxes may overlap | Error |
| R3 | Container title must clear children (5mm zone) | Warning |
| R4 | Box text must fit within padded inner area | Warning |
| R5 | Text-to-text margin >= 2mm | Error |
| R6 | Text-to-edge margin >= 2mm | Error |
| R7 | Arrow visible-length ratio >= 90% | Error |
| R8 | Curved-arrow label on same side as arc | Error |
| R9 | All elements within canvas bounds | Error |

## Auto-Fix

`auto_fix=True` on `render()` runs multi-pass fixing:

- **Phase 1** (pre-render): Container enclosure (R1), overlap resolution (R2), canvas bounds expansion (R9), arrow length adjustment, bidirectional arrow curving
- **Phase 2** (post-render): Text collision (R5/R6), arrow label occlusion (R7/R8)

Each fix is logged with per-element detail.

## Shapes

| Shape | Description |
|-------|-------------|
| `rounded` | Rounded rectangle (default) |
| `box` | Sharp-cornered rectangle |
| `stadium` | Pill-shaped |
| `cylinder` | Database cylinder |
| `document` | Paper with folded corner |
| `file` | Folder with tab |
| `codeblock` | Terminal window with title bar |

### Anchors

`top`, `bottom`, `left`, `right`, `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center`, `auto`. Aliases (`n`/`s`/`e`/`w`, `tl`/`br`, etc.) are normalized automatically.

### Element IDs

- **Boxes/Containers**: User-defined. Use `_box`/`_container` suffixes for searchability.
- **Arrows**: Auto-generated as `"arrow:source->target"`

## Architecture

```
_diagram/_diagram/
  _core.py         # Diagram builder class, render()
  _specs.py        # BoxSpec, ArrowSpec, IconSpec, PositionSpec dataclasses
  _validate.py     # Validation rules (R1-R9)
  _autofix.py      # Multi-pass auto-fix orchestrator
  _fix_layout.py   # Pre-render fixers (R1, R2, R9)
  _fix_arrows.py   # Arrow fixers (length, bidirectional, occlusion)
  _render.py       # Matplotlib rendering
  _io.py           # Serialization, render_to_file, watermark
  _debug.py        # Debug overlay image generation
  _color.py        # Color resolution and normalization
  _constants.py    # Anchor points, node classes, normalize_anchor()
  _flex.py         # CSS flexbox-like layout engine
  _layout.py       # auto_layout() algorithms
  _layout_graph.py # Graph-based container layout
  _hitmap.py       # Click-target hitmap generation
  _geom.py         # Geometry helpers
  _icons.py        # Icon support
  _codeblock.py    # Codeblock shape renderer
  _editor.py       # GUI editing support
  _overlap.py      # Overlap resolution logic
```

<!-- EOF -->

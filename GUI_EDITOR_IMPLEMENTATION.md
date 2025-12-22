# GUI Editor Implementation Checklist

## Phase 1: Core Infrastructure

- [x] **`_editor/__init__.py`** - Public API
  - [x] `edit()` function accepting RecordingFigure or recipe path
  - [x] Input type detection and handling
  - [x] Style loading integration

- [x] **`_editor/_hitmap.py`** - Hitmap Generation
  - [x] `generate_hitmap(fig, dpi)` - Main generation function
  - [x] `_id_to_rgb(element_id)` - Color encoding (first 12 distinct, then HSV)
  - [x] Element collection (lines, scatter, bars, fills, text)
  - [x] Color map dictionary creation
  - [x] Original property backup/restore

- [x] **`_editor/_bbox.py`** - Bounding Box Extraction
  - [x] `extract_bboxes(fig, ax, img_width, img_height)` - Single axis
  - [x] Coordinate transformation pipeline (display → image pixels)
  - [x] Support for: traces, scatter, bars, labels, legend, spines
  - [x] Points array extraction for line proximity detection

- [x] **`_editor/_renderer.py`** - Preview Rendering
  - [x] `render_preview(fig, overrides)` - Render with style overrides
  - [x] Style merging: base < loaded < overrides
  - [x] Integration with `apply_style_mm()`
  - [x] PNG buffer output

## Phase 2: Flask Application

- [x] **`_editor/_flask_app.py`** - Flask Routes
  - [x] `FigureEditor` class with state management
  - [x] `GET /` - Main editor page
  - [x] `GET /preview` - Initial figure preview
  - [x] `POST /update` - Re-render with overrides
  - [x] `GET /hitmap` - Hitmap image + color_map
  - [x] `POST /save` - Save style overrides
  - [x] `GET /download/<fmt>` - Download PNG/SVG/PDF
  - [x] Port conflict handling (auto-find available)
  - [x] Browser auto-open

- [x] **`_editor/_templates/__init__.py`** - Template Builder
  - [x] `build_html_template()` - Assemble full HTML
  - [x] Template injection (overrides, metadata)

## Phase 3: Templates

- [x] **`_editor/_templates/_html.py`** - HTML Structure
  - [x] Preview panel with image + SVG overlay
  - [x] Hidden hitmap canvas
  - [x] Controls panel sections:
    - [x] Selected Element info
    - [x] Dimensions (axes, margins, spacing)
    - [x] Fonts (family dropdown, all size fields)
    - [x] Lines & Markers
    - [x] Ticks (length, thickness, direction, n_ticks)
    - [x] Colors & Theme (mode toggle, palette pickers)
    - [x] Legend (frameon, loc, alpha, colors)
    - [x] Behavior flags (grid, spines, auto_scale)
    - [x] Output (dpi, transparent, format)
    - [x] Actions (Save, Reset, Download buttons)

- [x] **`_editor/_templates/_styles.py`** - CSS
  - [x] CSS variables for theming
  - [x] Light mode styles
  - [x] Dark mode styles (`[data-theme="dark"]`)
  - [x] Selection overlay styling
  - [x] Form control styling
  - [x] Responsive layout

- [x] **`_editor/_templates/_scripts.py`** - JavaScript
  - [x] `loadHitmap()` - Load to hidden canvas
  - [x] `getElementAtClick(x, y)` - Pixel sampling + lookup
  - [x] `updatePreview()` - POST to /update, refresh image
  - [x] `collectOverrides()` - Gather form values
  - [x] `saveOverrides()` - POST to /save
  - [x] Click coordinate transformation
  - [x] Element selection highlighting
  - [x] Form change handlers with debounce
  - [x] Theme toggle handler

## Phase 4: Integration

- [x] **Update `figrecipe/__init__.py`**
  - [x] Import `edit` from `_editor`
  - [x] Add to `__all__`

- [x] **Update `pyproject.toml`**
  - [x] Add Flask to optional dependencies (`[project.optional-dependencies]`)
  - [x] Create `editor` extras group

## Phase 4.5: Style Override Separation

- [x] **`_editor/_overrides.py`** - Layered Style Management
  - [x] `StyleOverrides` dataclass with base, programmatic, manual layers
  - [x] `get_effective_style()` - Merge all layers (base < programmatic < manual)
  - [x] `get_original_style()` - Get style without manual overrides
  - [x] `clear_manual_overrides()` - Restore to original
  - [x] `get_diff()` - Compare original vs manual
  - [x] Timestamp tracking for manual modifications
  - [x] JSON serialization/deserialization

- [x] **Update `_flask_app.py`** - Override Support
  - [x] `FigureEditor` uses `StyleOverrides` for state management
  - [x] `GET /style` - Return all style layers and metadata
  - [x] `POST /restore` - Clear manual overrides, return original
  - [x] `GET /diff` - Return difference between original and manual
  - [x] Save overrides to `.overrides.json` file

- [x] **Update Templates**
  - [x] "Restore" button in HTML
  - [x] Override status indicator (shows when manual overrides active)
  - [x] Warning button styling in CSS
  - [x] `restoreOriginal()` JavaScript function
  - [x] `checkOverrideStatus()` JavaScript function

## Phase 5: Testing & Polish

- [ ] Unit tests for hitmap color encoding/decoding
- [ ] Unit tests for bbox coordinate transformation
- [ ] Integration test: create figure → edit → verify
- [ ] Test with recipe file input
- [ ] Test dark mode rendering
- [ ] Test all property editors
- [ ] Documentation in docstrings

## Architecture Summary

```
figrecipe/_editor/
├── __init__.py          - edit(), public API
├── _hitmap.py           - Hitmap generation
├── _bbox.py             - Bounding box extraction
├── _flask_app.py        - Flask server & routes
├── _renderer.py         - Preview rendering
├── _overrides.py        - Layered style management (base/programmatic/manual)
└── _templates/
    ├── __init__.py      - Template builder
    ├── _html.py         - HTML structure
    ├── _styles.py       - CSS (light/dark)
    └── _scripts.py      - JavaScript
```

## Style Override Architecture

```
Priority (lowest to highest):
┌─────────────────────────┐
│   Base Style            │  ← From preset (e.g., SCITEX.yaml)
├─────────────────────────┤
│   Programmatic Style    │  ← From code (fr.load_style(), kwargs)
├─────────────────────────┤
│   Manual Overrides      │  ← From GUI editor (stored separately)
└─────────────────────────┘

Storage:
- recipe.yaml         → Figure recipe
- recipe.overrides.json → Manual overrides (timestamps, diff tracking)

Features:
- Restore to original (clear manual overrides)
- Compare changes (diff between original and manual)
- Timestamp tracking for manual modifications
```

## Usage

```python
import figrecipe as fr

# Edit live figure
fig, ax = fr.subplots()
ax.plot(x, y, id='data')
fr.edit(fig)

# Edit saved recipe
fr.edit('recipe.yaml')
```

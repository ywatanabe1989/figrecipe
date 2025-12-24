# Refactoring Status

## _scripts.py (3953 lines)

### Extracted Modules in `_templates/_scripts/`:
- [x] **_core.py** (223 lines) - State, initialization, utilities (showToast, debounce, scheduleUpdate)
- [x] **_zoom.py** (131 lines) - Zoom/pan controls and handlers
- [x] **_overlays.py** (292 lines) - Measurement overlays (ruler, grid, columns)
- [x] **_inspector.py** (315 lines) - Element inspector (Alt+I, Alt+Shift+I debug)
- [x] **_files.py** (144 lines) - File switching functionality
- [x] **_hitmap.py** (460 lines) - Hitmap loading, hit region drawing, element detection
- [x] **_selection.py** (210 lines) - Selection drawing, property sync
- [x] **_colors.py** (268 lines) - Color presets, conversion, input widget
- [x] **_element_editor.py** (242 lines) - Dynamic form fields, call properties
- [x] **_tabs.py** (78 lines) - Tab navigation (Figure/Axis/Element)
- [x] **_view_mode.py** (100 lines) - View mode management (all/selected)
- [x] **_modals.py** (200 lines) - Theme and shortcuts modals
- [x] **_api.py** (196 lines) - API calls (save, load, update, download)
- [x] **_labels.py** (350 lines) - Label inputs, axis type, legend position
- [x] **__init__.py** - Module exports (14 modules)

### Remaining in _scripts_main.py:
- initializeEventListeners, handleKeyboardShortcuts (initialization only)
- Some duplicate code that could be replaced with modular imports

### Notes
- Main _scripts_main.py still contains the complete working code
- _scripts/ modules are for incremental refactoring (14 modules extracted)
- Total extracted: ~2900 lines across 14 modules
- _templates/__init__.py imports from _scripts_main.py (not _scripts/)

---

## _bbox (formerly _bbox.py, 1311 lines)

### Status: Partially Refactored
Modular helper functions extracted to `_bbox/` package:

- [x] **_transforms.py** (129 lines) - Coordinate transformation utilities
- [x] **_elements.py** (145 lines) - General element, text, tick bbox extraction
- [x] **_lines.py** (164 lines) - Line and quiver bbox extraction
- [x] **_collections.py** (159 lines) - Collection and patch bbox extraction
- [x] **__init__.py** - Re-exports extract_bboxes from _bbox_main.py + helper functions

### Notes
- Main `extract_bboxes` function (725 lines) remains in `_bbox_main.py`
- `_bbox/` package re-exports `extract_bboxes` for backward compatibility
- Helper functions can now be imported individually for testing/reuse
- Further refactoring could split `extract_bboxes` into smaller functions

---

---

## _wrappers/_axes.py (1216→1079 lines)

### Status: In Progress
Extracting helper functions to reduce file size:

- [x] **_violin_helpers.py** - Violin inner plot helpers (box, swarm, stick, point)
- [x] **_plot_helpers.py** - Beeswarm positions, color helpers, KDE computation

### Notes
- Main RecordingAxes class contains complex plot methods (violinplot, joyplot, swarmplot)
- Violin inner helpers extracted to dedicated module
- Plot helpers extracted (beeswarm, colors)
- Need to: remove _beeswarm_positions method, update imports
- Further extraction needed to get under 512 lines

---

## Next Steps
1. Complete _axes.py refactoring (remove old helpers, add imports)
2. Continue with _hitmap.py refactoring
3. Delete this file when refactoring is complete

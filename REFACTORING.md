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
- [x] **__init__.py** - Module exports (individual modules, not combined SCRIPTS)

### Remaining in _scripts.py:
- initializeEventListeners, handleKeyboardShortcuts
- Labels (loadLabels, updateLabel)
- Element editor (showDynamicCallProperties, createDynamicField, color functions)
- Controls (tab switching, theme modal, download dropdown, label inputs)
- API calls (collectOverrides, resetValues, saveOverrides, downloadFigure)

### Notes
- Main _scripts.py still contains the complete working code
- _scripts/ modules are for incremental refactoring
- _templates/__init__.py imports from _scripts.py (not _scripts/)

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

## Next Steps
1. Continue extracting code from _scripts.py into modules
2. Create _bbox/ modular structure
3. Update imports to use modular files
4. Remove duplicate code from main files
5. Delete this file when refactoring is complete

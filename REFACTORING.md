# Refactoring: _scripts.py

## Context
`src/figrecipe/_editor/_templates/_scripts.py` is 3983 lines, exceeding the 512-line limit.

## Plan
Split into logical modules in `_templates/_scripts/`:

1. **_core.py** (~200 lines)
   - State initialization, global variables
   - Utility functions (showToast, debounce)

2. **_zoom.py** (~150 lines)
   - Zoom controls and handlers
   - Fit-to-view, zoom shortcuts

3. **_hitmap.py** (~300 lines)
   - Hit region drawing
   - Click detection and selection

4. **_controls.py** (~400 lines)
   - Form input handlers
   - Tab navigation
   - Theme/download controls

5. **_api.py** (~200 lines)
   - API calls (refresh, save, download)
   - File switching

6. **_element_editor.py** (~400 lines)
   - Dynamic element property editing
   - Call argument handlers

7. **_inspector.py** (~300 lines)
   - Element inspector (Alt+I)
   - Debug capture (Alt+Shift+I)

8. **_keyboard.py** (~150 lines)
   - Keyboard shortcuts
   - Modal handlers

9. **__init__.py**
   - Combines all script modules in correct order

## Status
- [ ] Create _scripts/ subdirectory
- [ ] Split into modules
- [ ] Update _html.py to use new module
- [ ] Delete this file

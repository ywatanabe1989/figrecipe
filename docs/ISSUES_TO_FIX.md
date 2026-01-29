# FigRecipe Reproduction Issues

## Summary

Issues identified from running `01_all_plots.py` with `reproduce=True`.

**Status Update (2026-01-26):** Most issues have been resolved. All 47 pixel-perfect tests pass.

---

## 1. clip_on Injection Errors (RESOLVED ✓)

**Status**: FIXED
**Severity**: High - Prevents plotting

### Affected Methods:
- `stem` - FIXED
- `streamplot` - FIXED
- `contour` - WARNING only (acceptable)

### Fix Applied:
Updated CLIP_ON_SUPPORTED_METHODS to exclude unsupported methods.

---

## 2. imshow Replay Error (RESOLVED ✓)

**Status**: FIXED
**Severity**: Medium - Image not reproduced

### Fix Applied:
Arrays are now properly converted to numeric dtype during CSV loading with dtype preservation.

---

## 3. Colorbar Not Reproduced (MISSING)

**Status**: Colorbar completely missing in reproduced figures
**Severity**: High - Visual mismatch

### Affected Methods:
- `imshow`
- `pcolormesh`
- `contourf`
- `hexbin`
- `hist2d`
- `matshow`
- All 2D plots with colorbars

### Expected Behavior:
- Original figure has colorbar (e.g., matshow shows colorbar on right)
- Reproduced figure should also have colorbar in same position

### Current Behavior:
- Reproduced figure has NO colorbar at all

### Root Cause:
`_auto_add_colorbars()` in `_reproducer/_core.py` checks for `colorbar.auto: true` in style, but:
1. The colorbar style may not be in the recipe
2. The check may not find the loaded style correctly
3. Or the function is not being called at all

### Location:
- `src/figrecipe/_reproducer/_core.py` - `_auto_add_colorbars()` function (line ~380)

### Fix:
1. Debug why `_auto_add_colorbars()` is not adding colorbars
2. May need to record colorbar explicitly in recipe instead of auto-adding

---

## 4. boxplot Color Replay Error (RESOLVED ✓)

**Status**: FIXED
**Severity**: Low - Already has handler but still warns

### Fix Applied:
Boxplot handler now properly routes `color` kwarg through the dedicated boxplot replay handler.

---

## 5. SCITEX Styling Not Applied (VISUAL)

**Status**: Reproduced figures have wrong styling
**Severity**: Medium - Visual mismatch

### Symptoms:
- Top/right spines visible (should be hidden)
- Wrong font sizes
- Wrong tick styling

### Root Cause:
Style may not be applied correctly during `reproduce_from_record()`.

### Location:
- `src/figrecipe/_reproducer/_core.py` - `apply_style_mm()` call
- `src/figrecipe/styles/_style_applier.py`

### Fix:
Ensure style is fully applied including spine visibility.

---

## 6. quiver Memory Error (FAILING)

**Status**: Test failing
**Severity**: Medium

### Error:
```
[31/47] quiver: FAILED - std::bad_alloc
```

### Root Cause:
Memory allocation failure, possibly due to large arrow dataset.

### Location:
- `src/figrecipe/_dev/_plotters.py` - quiver demo

### Fix:
Reduce data size for quiver demo.

---

## Test Results Summary (Updated 2026-01-26)

```
# Pixel-perfect tests: ALL PASS
tests/test_pixel_perfect.py - 47 passed

# Data serialization tests: ALL PASS
tests/test_data_serialization.py - 99 passed

# Editor hitmap tests: ALL PASS
tests/test_editor_hitmap.py - 96 passed, 3 skipped

# Hitmap detection tests: ALL PASS
tests/test_hitmap_call_id_matching.py + test_hitmap_pixel_detection.py - 36 passed, 2 xfailed
```

---

---

## 7. Violin Plot Inner Box Styling (VISUAL)

**Status**: Wrong styling
**Severity**: Medium - Visual mismatch

### Current Behavior:
- Inner box is BLACK filled
- Median shown as white dot

### Expected Behavior:
- Inner box should be GRAY filled
- Median should be BLACK LINE with 0.2mm thickness

### Location:
- `src/figrecipe/_wrappers/_violin_helpers.py`
- `src/figrecipe/_wrappers/_axes_plots.py`
- `src/figrecipe/styles/presets/SCITEX.yaml` - violinplot settings

### Fix:
Change inner box fill to gray, median to black line with 0.2mm thickness.

---

## Priority Order

1. **clip_on injection** - Causing test failures
2. **Colorbar reproduction** - Major visual issue
3. **imshow dtype** - Image not reproduced
4. **SCITEX styling** - Visual mismatch
5. **Violin box styling** - Visual mismatch
6. **boxplot color** - Minor warning
7. **quiver memory** - Demo-only issue

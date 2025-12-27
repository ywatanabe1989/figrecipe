# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2025-12-28

### Added
- **GUI PORT configuration** - `make gui PORT=5051` to specify custom port (default: 5050)
- **Click sound effects** - Browser demo recordings now include click sounds
- **Narration utilities export** - `extract_captions_from_script`, `add_narration_to_video` in browser module

### Changed
- **Demo recording improvements** - Color change and panel drag demos with better cursor synchronization
- **Video trimming margins** - Adjusted trim margins for cleaner demo output (1.5s start, 1s end)
- **Narration settings** - Lower BGM volume (0.08), longer fade-out (2s)

## [0.8.0] - 2025-12-27

### Added
- **Statistical annotations** - `fr.stats.add_significance()` for adding p-value annotations
- **p-value formatting** - `p_to_stars()` converts p-values to significance stars (*, **, ***, n.s.)
- **Smart alignment** - `fr.composition.smart_align()` for automatic panel alignment with asymmetric margins

### Fixed
- **Stats test assertions** - Correct n.s. assertion in p_to_stars test
- **Composition margins** - Use asymmetric margin variables in smart_align

## [0.7.6] - 2025-12-27

### Added
- **Demo movie infrastructure** - Automated recording and processing of demo videos
- **Full HD recording** - 1920x1080 resolution for demo videos
- **Timing metadata** - Automatic `.timing.json` generation for precise TTS sync
- **Parallel processing** - `process_all_demos.py` with `--workers` option
- **TTS integration** - ElevenLabs with gTTS fallback for narration
- **BGM support** - Background music with fade in/out effects

### Changed
- **README improvements** - Collapsible sections, enhanced readability

## [0.7.5] - 2025-12-25

### Added
- **Panel snapping** - Snap to grid (5mm), panel edges, and centers during drag
- **Magnetic attraction** - Panels slow down and "stick" as they approach snap targets
- **Visual alignment guides** - Orange/purple lines with opacity indicating proximity
- **Alt+Drag fine control** - Hold Alt to disable snapping for precise positioning

## [0.7.4] - 2025-12-25

### Added
- **Click priority z-index** - Scatter/legend have highest click priority, axes lowest
- **Legend drag-to-move** - Drag legends to reposition with x,y coordinates
- **Expanded panel bounds** - Panel drag includes title/label areas (15mm left, 8mm top, 12mm bottom margins)

### Fixed
- **Coordinate precision** - Legend drag uses upper-left corner for precise bbox_to_anchor positioning
- **Demo plot legend** - Added legend to plot demo for testing

## [0.7.3] - 2025-12-25

### Added
- **Panel drag-to-move** - Drag panels directly without modifier keys
- **mm coordinates** - Panel positions use mm units with upper-left origin
- **Restore positions** - Restore button now restores original panel coordinates
- **Server timestamp** - Debug timestamp visible in editor header

### Fixed
- **Container ID fix** - Fixed drag initialization (preview-container → zoom-container)
- **Null overlay check** - Added safety checks for drag overlay element

## [0.7.2] - 2025-12-25

### Added
- **Panel position editing** - View and edit panel positions numerically

## [0.7.1] - 2025-12-24

### Added
- **Panel selection** - Click to select panels in figure editor

## [0.7.0] - 2025-12-24

### Added
- **Hitmap improvements** - Enhanced element hit detection

## [0.6.0] - 2025-12-23

### Added
- **`ax.joyplot()`** - Ridgeline/joyplot visualization with KDE-based density estimation
- **`ax.swarmplot()`** - Beeswarm plot with non-overlapping point positioning
- **Theme switching** - Switch between SCITEX/MATPLOTLIB presets with live preview in editor
- **Theme CRUD** - View theme content, download as YAML, copy to clipboard
- **Legend controls** - Show/hide toggle, location dropdown, xy coordinate positioning
- **scipy dependency** - Added scipy>=1.7.0 for joyplot KDE computation

### Changed
- **Editor layout** - Moved axes size (width_mm, height_mm) from Figure tab to Axis tab

### Fixed
- **Tick direction validation** - Empty tick direction values no longer cause errors
- **Theme CommentedMap handling** - Fixed TypeError when switching themes with ruamel.yaml

## [0.5.1] - 2025-12-22

### Fixed
- **Dark theme colors** - Fixed typo in SCITEX preset: text/spine/tick now all use "#d4d4d4"
- **GitHub Actions CI** - Added automated testing workflow for Python 3.9-3.12

### Added
- **Example outputs** - Added `outputs/notebook/` with pre-generated example figures
- **Style presets tracked** - SCITEX.yaml and MATPLOTLIB.yaml now tracked in repo

## [0.5.0] - 2025-12-22

### Added
- **`fr.crop()`** - Crop images to content with mm-based margins
- **`validate_error_level` parameter** - Configurable validation handling:
  - `"error"` (default): Raise ValueError on validation failure
  - `"warning"`: Print warning but continue
  - `"debug"`: Silent, check result programmatically
- **Optional extras documentation** - README now documents `pip install figrecipe[seaborn,imaging,all]`

### Changed
- **`save()` API refactored** - Now returns `(image_path, yaml_path, result)` tuple
- **Path extension controls format** - `.png`, `.pdf`, `.svg`, `.jpg` supported
- **Default DPI** - Changed from 100 to 300 for publication quality
- **Development Status** - Updated from Alpha to Beta
- **Validation message** - "Validation: PASSED" → "Reproducible Validation: PASSED"

### Fixed
- **Legend styling in dark mode** - Font size, background color, and text color now applied via rcParams
- **`unload_style()` reset** - Now properly resets matplotlib rcParams to defaults
- **SCITEX preset alias** - Fixed alias direction (FIGRECIPE → SCITEX)
- **FTS typo** - "Statics" → "Statistics"

## [0.3.4] - 2025-12-21

### Added
- **Style presets** - Built-in style presets for easy switching:
  - `SCIENTIFIC` (default): Publication-quality with colorblind-friendly Wong 2011 palette
  - `MINIMAL`: Clean, minimal design with grayscale emphasis
  - `PRESENTATION`: Large fonts and bold lines for slides
- **`ps.list_presets()`** - List all available style presets
- **Custom YAML styles** - Load your own style files: `ps.load_style("/path/to/style.yaml")`
- **Reproducibility validation** - Validate recipe reproduces original figure:
  - `ps.save(fig, path, validate=True)` - Validate on save
  - `ps.validate(path)` - Standalone validation
  - Returns `ValidationResult` with MSE, dimensions, PSNR
- **Layout recording** - `subplots_adjust` parameters now recorded for pixel-perfect reproduction
- **Style recording** - Style parameters recorded and re-applied during reproduction

### Changed
- Renamed brand-specific "SCITEX" references to generic "SCIENTIFIC" preset
- `ps.load_style()` now accepts preset names: `ps.load_style("MINIMAL")`
- Default style is now the SCIENTIFIC preset

### Fixed
- **Pixel-perfect reproduction** - MM-layout and styled figures now reproduce with MSE=0

## [0.3.2] - 2025-12-21

### Added
- **Colorblind-friendly color palette** - Scientific color palette automatically applied via rcParams
  - Blue (#0072B2), Orange (#D55E00), Green (#009E73), Purple (#CC79A7), etc.
  - Access via `style.colors.palette` or auto-cycling in plots
- **Transparent background** - Default light theme now uses transparent background

### Fixed
- **Title overlap in multi-panel figures** - Added proper `subplots_adjust()` based on mm layout parameters
- **n_ticks** - Changed default from 5 to 4 for cleaner tick labels

### Changed
- Style applier now sets matplotlib color cycle from style palette

## [0.3.1] - 2025-12-21

### Fixed
- **Seaborn duplicate recording** - Seaborn calls no longer record underlying matplotlib calls (e.g., `ax.scatter()` from `sns.scatterplot()`)
- **Seaborn sizes parameter** - `sizes=(min, max)` tuples now correctly serialize and deserialize, fixing the legend reproduction issue where all size values were listed instead of grouped ranges

## [0.3.0] - 2025-12-21

### Added
- **MM-based layout system** for publication-quality figures
  - `axes_width_mm`, `axes_height_mm` parameters for precise axes sizing
  - `margin_left_mm`, `margin_right_mm`, `margin_bottom_mm`, `margin_top_mm` for margins
  - `space_w_mm`, `space_h_mm` for spacing between axes in multi-panel figures
- **Style system** inspired by SciTeX
  - `ps.load_style()` to load style configuration from YAML
  - `ps.apply_style()` to apply publication-quality styling to axes
  - `ps.STYLE` proxy for quick access to default style
  - `FIGRECIPE_STYLE.yaml` default configuration with:
    - Font sizes (axis labels, tick labels, title, legend)
    - Line thicknesses in mm
    - Tick parameters in mm
    - Theme support (light/dark mode)
- **Unit conversion utilities**
  - `ps.mm_to_inch()`, `ps.inch_to_mm()`
  - `ps.mm_to_pt()`, `ps.pt_to_mm()`
- Example `06_mm_layout_and_style.py` demonstrating new features

### Changed
- `ps.subplots()` now accepts mm-based layout parameters
- `ps.subplots()` accepts `apply_style_mm=True` for automatic style application
- Version updated to 0.3.0

## [0.2.0] - 2025-12-21

### Added
- CHANGELOG.md for tracking version history
- Version bump for PyPI publication

### Changed
- Version updated to 0.2.0

## [0.1.0] - 2025-12-21

### Added
- Core recording functionality via `ps.subplots()` wrapper
- YAML-based recipe format for figure serialization
- `ps.save()` function to export figures as recipes
- `ps.reproduce()` function to recreate figures from recipes
- `ps.info()` function to inspect recipe metadata
- CSV as default data format for human readability
- NPZ format support for binary data storage
- External data file support for large arrays (>100 elements)
- Custom call IDs for identifying plot elements
- Selective call reproduction via `calls` parameter
- Seaborn integration (`ps.sns.scatterplot()`, `ps.sns.lineplot()`, etc.)
- DataFrame column serialization for seaborn plots
- Makefile for common development tasks
- Comprehensive test suite (40 tests)
- Example scripts demonstrating core functionality

### Supported matplotlib methods
- `plot()` - line plots
- `scatter()` - scatter plots
- `bar()`, `barh()` - bar charts
- `fill_between()` - filled areas
- `step()` - step plots
- `errorbar()` - error bar plots
- `hist()` - histograms
- `imshow()` - image display
- `contour()`, `contourf()` - contour plots
- `set_xlabel()`, `set_ylabel()`, `set_title()` - decorations
- `legend()`, `grid()` - additional decorations

### Supported seaborn functions
- `scatterplot()` - scatter plots with hue/size support
- `lineplot()` - line plots with confidence intervals
- Additional functions available but may need further testing

[0.8.1]: https://github.com/ywatanabe1989/figrecipe/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.7.6...v0.8.0
[0.7.6]: https://github.com/ywatanabe1989/figrecipe/compare/v0.7.5...v0.7.6
[0.6.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/ywatanabe1989/figrecipe/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.4...v0.5.0
[0.3.4]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.2...v0.3.4
[0.3.2]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ywatanabe1989/figrecipe/releases/tag/v0.1.0

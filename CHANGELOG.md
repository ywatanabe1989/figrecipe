# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.5.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.4...v0.5.0
[0.3.4]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.2...v0.3.4
[0.3.2]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/ywatanabe1989/figrecipe/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ywatanabe1989/figrecipe/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ywatanabe1989/figrecipe/releases/tag/v0.1.0

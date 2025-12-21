# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  - `PLOTSPEC_STYLE.yaml` default configuration with:
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

[0.3.0]: https://github.com/ywatanabe1989/plotspec/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ywatanabe1989/plotspec/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ywatanabe1989/plotspec/releases/tag/v0.1.0

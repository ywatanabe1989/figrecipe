# plotspec

**Record and reproduce matplotlib figures.**

[![PyPI version](https://badge.fury.io/py/plotspec.svg)](https://badge.fury.io/py/plotspec)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

plotspec captures matplotlib plotting calls and saves them as human-readable YAML "recipes" that can be used to reproduce figures exactly.

## Example Output

<table>
<tr>
<td><strong>Original</strong></td>
<td><strong>Reproduced from Recipe</strong></td>
</tr>
<tr>
<td><img src="outputs/examples/06_mm_layout_original.png" width="300"/></td>
<td><img src="outputs/examples/06_mm_layout_reproduced.png" width="300"/></td>
</tr>
</table>

**Multi-panel figures with publication-quality styling:**

<img src="outputs/examples/06_mm_layout_multi.png" width="400"/>

## Features

- **Drop-in replacement**: Use `ps.subplots()` instead of `plt.subplots()`
- **Automatic tracking**: All plotting calls are recorded automatically
- **YAML recipes**: Human-readable format for figure specifications
- **Efficient storage**: Large arrays saved to separate CSV/NPZ files
- **One-line reproduction**: `fig, ax = ps.reproduce("figure.yaml")`
- **Selective replay**: Reproduce only specific plotting calls
- **MM-based layout**: Precise control with millimeter-based sizing
- **Publication styling**: SCITEX-inspired color palette and styling
- **Seaborn support**: Record and reproduce seaborn plots

## Installation

```bash
pip install plotspec
```

## Quick Start

### Recording a Figure

```python
import plotspec as ps
import numpy as np

# Create data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create figure (drop-in replacement for plt.subplots)
fig, ax = ps.subplots()

# Plot as usual - calls are recorded automatically
ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
ax.scatter(x[::10], y[::10], s=50, color='blue', id='peaks')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')
ax.set_title('Sine Wave Example')
ax.legend()

# Save the recipe
ps.save(fig, 'sine_wave.yaml')
```

### Reproducing a Figure

```python
import plotspec as ps
import matplotlib.pyplot as plt

# Reproduce the entire figure
fig, ax = ps.reproduce('sine_wave.yaml')
plt.show()

# Or reproduce only specific calls
fig, ax = ps.reproduce('sine_wave.yaml', calls=['sine_wave'])
plt.show()
```

### Publication-Quality Figures with MM Layout

```python
import plotspec as ps
import numpy as np

# Load SCITEX-style configuration
style = ps.load_style()

# Create figure with precise mm-based dimensions
fig, ax = ps.subplots(
    axes_width_mm=60,       # 60mm wide axes
    axes_height_mm=40,      # 40mm tall axes
    margin_left_mm=15,      # Space for y-axis labels
    margin_bottom_mm=12,    # Space for x-axis labels
    apply_style_mm=True,    # Apply publication style
)

# Plot with auto-cycling SCITEX colors
x = np.linspace(0, 2*np.pi, 100)
ax.plot(x, np.sin(x), label='sin(x)')  # Auto: SCITEX blue
ax.plot(x, np.cos(x), label='cos(x)')  # Auto: SCITEX orange

ax.set_xlabel('x (radians)')
ax.set_ylabel('y')
ax.legend()

# Save with transparent background
fig.fig.savefig('publication_figure.png', dpi=300, transparent=True)
ps.save(fig, 'publication_figure.yaml')
```

### Inspecting a Recipe

```python
import plotspec as ps

# Get recipe information without reproducing
info = ps.info('sine_wave.yaml')
print(f"Created: {info['created']}")
print(f"Figure size: {info['figsize']}")
print(f"Number of calls: {len(info['calls'])}")

for call in info['calls']:
    print(f"  - {call['id']}: {call['function']}()")
```

## Recipe Format

Recipes are saved as YAML files:

```yaml
plotspec: "1.0"
id: fig_a1b2c3d4
created: "2025-12-21T14:30:00"
matplotlib_version: "3.8.0"

figure:
  figsize: [10, 6]
  dpi: 100

axes:
  ax_0_0:
    calls:
      - id: sine_wave
        function: plot
        args:
          - name: x
            data: sine_wave_data/sine_wave_x.csv
          - name: y
            data: sine_wave_data/sine_wave_y.csv
        kwargs:
          color: "#0072B2"
          linewidth: 2

    decorations:
      - id: set_xlabel_000
        function: set_xlabel
        args:
          - name: arg0
            data: "Time (s)"
        kwargs: {}
```

## Advanced Usage

### Custom Call IDs

Use the `id` parameter to give meaningful names to your plots:

```python
ax.plot(x, y, color='red', id='experimental_data')
ax.plot(x, y_fit, color='blue', id='fitted_curve')
```

### Multiple Subplots

```python
fig, axes = ps.subplots(2, 2, figsize=(12, 10))
axes[0][0].plot(x, y1, id='top_left')
axes[0][1].scatter(x, y2, id='top_right')
axes[1][0].bar(categories, values, id='bottom_left')
axes[1][1].hist(data, id='bottom_right')
ps.save(fig, 'multi_panel.yaml')
```

### Seaborn Integration

```python
import plotspec as ps
import pandas as pd

df = pd.DataFrame({'x': x, 'y': y, 'category': categories})

fig, ax = ps.subplots()
ps.sns.scatterplot(data=df, x='x', y='y', hue='category', ax=ax, id='scatter')
ps.save(fig, 'seaborn_figure.yaml')
```

### Temporarily Disable Recording

```python
fig, ax = ps.subplots()

# Recorded
ax.plot(x, y, id='main_data')

# Not recorded
with ax.no_record():
    ax.axhline(0, color='gray', linestyle='--')

# Recorded again
ax.scatter(x_points, y_points, id='highlights')
```

## Style Configuration

plotspec includes a configurable style system via `PLOTSPEC_STYLE.yaml`:

```python
import plotspec as ps

# Load and inspect style
style = ps.load_style()
print(f"Axes width: {style.axes.width_mm} mm")
print(f"Font: {style.fonts.family}")
print(f"Colors: {style.colors.palette[:4]}")

# Use style parameters directly
fig, ax = ps.subplots(**style.to_subplots_kwargs())
```

### SCITEX Color Palette

Colorblind-friendly scientific colors:
- Blue: `#0072B2`
- Orange: `#D55E00`
- Green: `#009E73`
- Purple: `#CC79A7`
- Yellow: `#F0E442`
- Cyan: `#56B4E9`

## Why plotspec?

### Scientific Reproducibility

Share the exact specification of your figures alongside your papers. Reviewers and readers can reproduce your figures exactly.

### Version Control Friendly

YAML recipes are human-readable and diff-friendly, making it easy to track changes to figures in git.

### Data Separation

Large arrays are automatically saved to efficient CSV or NPZ files, keeping recipes small and readable while preserving full data fidelity.

### Collaboration

Share figure "recipes" with collaborators who can modify and re-run them with their own data or styling preferences.

## API Reference

### Main Functions

- `ps.subplots(nrows=1, ncols=1, **kwargs)` - Create recording-enabled figure
- `ps.save(fig, path)` - Save figure recipe to YAML
- `ps.reproduce(path, calls=None)` - Reproduce figure from recipe
- `ps.info(path)` - Get recipe information
- `ps.load(path)` - Load recipe as FigureRecord object

### Style Functions

- `ps.load_style(path=None)` - Load style configuration
- `ps.apply_style(ax, style=None)` - Apply styling to axes
- `ps.STYLE` - Global style proxy object

### Unit Conversions

- `ps.mm_to_inch(mm)` - Convert mm to inches
- `ps.mm_to_pt(mm)` - Convert mm to points
- `ps.inch_to_mm(inch)` - Convert inches to mm
- `ps.pt_to_mm(pt)` - Convert points to mm

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

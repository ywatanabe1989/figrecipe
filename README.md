# plotspec

**Record and reproduce matplotlib figures.**

[![PyPI version](https://badge.fury.io/py/plotspec.svg)](https://badge.fury.io/py/plotspec)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

plotspec captures matplotlib plotting calls and saves them as human-readable YAML "recipes" that can be used to reproduce figures exactly.

## Features

- **Drop-in replacement**: Use `mpr.subplots()` instead of `plt.subplots()`
- **Automatic tracking**: All plotting calls are recorded automatically
- **YAML recipes**: Human-readable format for figure specifications
- **Efficient storage**: Large arrays saved to separate `.npy` files
- **One-line reproduction**: `fig, ax = ps.reproduce("figure.yaml")`
- **Selective replay**: Reproduce only specific plotting calls

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
mpr.save(fig, 'sine_wave.yaml')
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
            data: sine_wave_data/sine_wave_x.npz
          - name: y
            data: sine_wave_data/sine_wave_y.npz
        kwargs:
          color: red
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
mpr.save(fig, 'multi_panel.yaml')
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

## Why plotspec?

### Scientific Reproducibility

Share the exact specification of your figures alongside your papers. Reviewers and readers can reproduce your figures exactly.

### Version Control Friendly

YAML recipes are human-readable and diff-friendly, making it easy to track changes to figures in git.

### Data Separation

Large arrays are automatically saved to efficient `.npz` files, keeping recipes small and readable while preserving full data fidelity.

### Collaboration

Share figure "recipes" with collaborators who can modify and re-run them with their own data or styling preferences.

## API Reference

### Main Functions

- `mpr.subplots(nrows=1, ncols=1, **kwargs)` - Create recording-enabled figure
- `mpr.save(fig, path)` - Save figure recipe to YAML
- `mpr.reproduce(path, calls=None)` - Reproduce figure from recipe
- `mpr.info(path)` - Get recipe information
- `mpr.load(path)` - Load recipe as FigureRecord object

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

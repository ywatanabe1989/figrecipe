<p align="center">
  <img src="docs/figrecipe_logo.png" alt="figrecipe logo" width="200"/>
</p>

# figrecipe

Record and reproduce matplotlib figures with YAML recipes.

[![PyPI version](https://badge.fury.io/py/figrecipe.svg)](https://badge.fury.io/py/figrecipe)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Installation

```bash
pip install figrecipe
```

## Usage

### Recording

```python
import figrecipe as fr
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = fr.subplots()
ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')

fr.save(fig, 'figure.yaml')
```

### Reproducing

```python
import figrecipe as fr

fig, ax = fr.reproduce('figure.yaml')
```

### Drop-in replacement

```python
import figrecipe.plt as plt

fig, ax = plt.subplots()
ax.plot(x, y)
fig.savefig('figure.png')  # Auto-saves figure.yaml alongside
```

### Data extraction

```python
import figrecipe as fr

data = fr.extract_data('figure.yaml')
# Returns: {'sine_wave': {'x': array([...]), 'y': array([...])}}
```

### MM-based layout

```python
fig, ax = fr.subplots(
    axes_width_mm=60,
    axes_height_mm=40,
    margin_left_mm=15,
    margin_bottom_mm=12,
)
```

### Style presets

```python
fr.list_presets()  # ['DEFAULT', 'SCIENTIFIC', 'MINIMAL', 'PRESENTATION']
style = fr.load_style('SCIENTIFIC')
fig, ax = fr.subplots(**style.to_subplots_kwargs())
```

## Recipe format

```yaml
figrecipe: "1.0"
figure:
  figsize: [10, 6]
axes:
  ax_0_0:
    calls:
      - id: sine_wave
        function: plot
        args:
          - {name: x, data: sine_wave_x.csv}
          - {name: y, data: sine_wave_y.csv}
        kwargs:
          color: red
          linewidth: 2
```

## API

| Function | Description |
|----------|-------------|
| `fr.subplots()` | Create recording-enabled figure |
| `fr.save(fig, path)` | Save recipe |
| `fr.reproduce(path)` | Reproduce figure from recipe |
| `fr.extract_data(path)` | Extract plotted data from recipe |
| `fr.info(path)` | Get recipe metadata |
| `fr.load_style(name)` | Load style preset |
| `fr.list_presets()` | List available presets |

## License

AGPL-3.0 - see [LICENSE](LICENSE).

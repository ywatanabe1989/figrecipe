---
name: scientific-figure-patterns
description: ALWAYS invoke when implementing publication-quality comparison plots, multi-panel layouts, shared color scales, shared time axes, or PDF report assembly with figrecipe/matplotlib. Concrete code patterns implementing the universal rules in `scitex/general/30_scientific-figures.md`.
---

# Scientific Figure Patterns (figrecipe / matplotlib)

Implementation patterns for the universal scientific-figure rules at
[../general/30_scientific-figures.md](../general/30_scientific-figures.md).

## Comparison plot with shared color scale + single colorbar

```python
import matplotlib.pyplot as plt

# 1. Compute the global scale across BOTH conditions BEFORE plotting
vmin = min(data_a.min(), data_b.min())
vmax = max(data_a.max(), data_b.max())

# 2. Symmetric range for diverging data
vabs = max(abs(vmin), abs(vmax))
kw = dict(vmin=-vabs, vmax=vabs, cmap='RdBu_r')

# 3. Shared axes; side-by-side layout
fig, (ax_a, ax_b) = plt.subplots(1, 2, sharex=True, sharey=True,
                                  figsize=(10, 4))
im_a = ax_a.imshow(data_a, **kw); ax_a.set_title("Condition A")
im_b = ax_b.imshow(data_b, **kw); ax_b.set_title("Condition B")

# 4. ONE shared colorbar for the comparison group
fig.colorbar(im_a, ax=[ax_a, ax_b], label="value (units)")

# 5. Drop redundant inner labels (sharey already removes inner ticks)
ax_b.tick_params(labelleft=False)
```

Notes:
- `vmin`/`vmax` MUST be computed across all compared arrays — never per-axis.
- For sequential (non-diverging) data drop the symmetric step and use
  `cmap='viridis'`.

## Stacked plot with shared time axis (heatmap + averaged profile)

```python
fig, (ax_heat, ax_line) = plt.subplots(
    2, 1,
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]},
    figsize=(10, 5),
)

ax_heat.imshow(channels_x_time, aspect='auto')
ax_heat.tick_params(labelbottom=False)        # hide x labels on upper panel

ax_line.plot(t, channels_x_time.mean(axis=0))
ax_line.set_xlabel("time (s)")
fig.align_ylabels([ax_heat, ax_line])
```

## Multi-panel per-subject report grid

```python
fig, axes = plt.subplots(2, 3, sharex=True, sharey=True, figsize=(12, 8))
for ax, (cond, arr) in zip(axes.flat, conditions.items()):
    ax.imshow(arr, vmin=-vabs, vmax=vabs, cmap='RdBu_r')
    ax.set_title(cond)
fig.colorbar(axes[0, 0].images[0], ax=axes.ravel().tolist(),
             label="value (units)")
fig.align_ylabels(axes[:, 0])
fig.align_xlabels(axes[-1, :])
```

## PDF report assembly with bookmarks + size budget

```python
from fpdf import FPDF
from PIL import Image

PAGE_W = 10  # inches
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

for section_name, fig_paths in sections.items():
    pdf.add_page()
    pdf.start_section(section_name, level=0)        # PDF bookmark
    for fig_path in fig_paths:
        # Preserve original aspect ratio
        w, h = Image.open(fig_path).size
        page_h = PAGE_W * h / w
        pdf.image(fig_path, w=PAGE_W * 25.4, h=page_h * 25.4)  # in -> mm

pdf.output("report.pdf")
```

If the PDF exceeds the 10MB email limit, post-process with ghostscript:

```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook \
   -o report-compressed.pdf report.pdf
```

## Bookmarks via post-hoc pikepdf (when fpdf2 isn't available)

```python
import pikepdf
with pikepdf.open("report.pdf") as pdf:
    with pdf.open_outline() as outline:
        outline.root.extend([
            pikepdf.OutlineItem("Executive Summary", 0),
            pikepdf.OutlineItem("Methods", 1),
            pikepdf.OutlineItem("Results", 3),
        ])
    pdf.save("report-bookmarked.pdf")
```

## Common pitfalls

- Calling `imshow` without `vmin`/`vmax` — matplotlib auto-scales per call,
  destroying cross-panel comparability.
- Using `plt.colorbar(im_a)` (single-axes form) on a side-by-side comparison
  — produces an ugly colorbar attached only to the left panel. Use the
  multi-axes form `fig.colorbar(im_a, ax=[ax_a, ax_b])`.
- Setting `figsize` per panel and discovering the colorbar overlaps content
  — use `constrained_layout=True` or `fig.tight_layout()` after colorbar.
- Forgetting `fig.align_ylabels()` / `align_xlabels()` on multi-panel grids
  — y-labels at different x-positions look cluttered.

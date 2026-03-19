---
name: plot-types
description: Available plot types in figrecipe and when to use each.
---

# Plot Types Reference

## Standard matplotlib plots (via MCP)

| Plot Type | MCP Tool | Use When |
|-----------|----------|----------|
| `line` | `plt_line` / `plt_plot` | Time series, trends |
| `scatter` | `plt_scatter` | Relationships between variables |
| `bar` | `plt_bar` | Comparing categories |
| `barh` | `plt_barh` | Horizontal bar comparison |
| `hist` | `plt_hist` | Distribution of one variable |
| `hist2d` | `plt_hist2d` | Joint distribution |
| `boxplot` | `plt_boxplot` | Distribution comparison |
| `violinplot` | `plt_violinplot` | Distribution shape comparison |
| `pie` | `plt_pie` | Part-of-whole |
| `errorbar` | `plt_errorbar` | Data with uncertainty |
| `fill_between` | `plt_fill_between` | Confidence bands |
| `stackplot` | `plt_stackplot` | Cumulative composition |
| `contour` | `plt_contour` / `plt_contourf` | 2D scalar fields |
| `imshow` | `plt_imshow` | Images, heatmaps |
| `pcolormesh` | `plt_pcolormesh` | Non-uniform 2D grids |
| `quiver` | `plt_quiver` | Vector fields |
| `streamplot` | `plt_streamplot` | Flow fields |
| `stem` | `plt_stem` | Discrete signals |
| `stairs` | `plt_stairs` | Step functions |
| `hexbin` | `plt_hexbin` | Large scatter → density |
| `ecdf` | `plt_ecdf` | Empirical CDF |

## SciTeX-specific plot types

| Plot Type | MCP Tool | Use When |
|-----------|----------|----------|
| `stx_heatmap` | `plt_stx_heatmap` | Annotated heatmap / confusion matrix style |
| `stx_conf_mat` | `plt_stx_conf_mat` | Confusion matrix |
| `stx_line` | `plt_stx_line` | Line with SciTeX styling |
| `stx_scatter_hist` | `plt_stx_scatter_hist` | Scatter with marginal histograms |
| `stx_violin` | `plt_stx_violin` | Violin with individual points |
| `stx_mean_ci` | `plt_stx_mean_ci` | Mean with confidence interval |
| `stx_mean_std` | `plt_stx_mean_std` | Mean with standard deviation |
| `stx_median_iqr` | `plt_stx_median_iqr` | Median with IQR |
| `stx_shaded_line` | `plt_stx_shaded_line` | Line with shaded error band |
| `stx_raster` | `plt_stx_raster` | Spike raster plot |
| `stx_ecdf` | `plt_stx_ecdf` | Empirical CDF with SciTeX style |
| `stx_fillv` | `plt_stx_fillv` | Vertical fill regions |
| `stx_image` | `plt_stx_image` | Image display with scale bar |
| `stx_rectangle` | `plt_stx_rectangle` | Annotated rectangle regions |

## Spectral analysis plots

| Plot Type | MCP Tool | Use When |
|-----------|----------|----------|
| `psd` | `plt_psd` | Power spectral density |
| `csd` | `plt_csd` | Cross spectral density |
| `specgram` | `plt_specgram` | Spectrogram |
| `cohere` | `plt_cohere` | Coherence |
| `acorr` | `plt_acorr` | Autocorrelation |
| `xcorr` | `plt_xcorr` | Cross-correlation |
| `magnitude_spectrum` | `plt_magnitude_spectrum` | Frequency magnitude |
| `phase_spectrum` | `plt_phase_spectrum` | Frequency phase |
| `angle_spectrum` | `plt_angle_spectrum` | Angle spectrum |

## Choosing the right plot

1. **One variable distribution**: `hist`, `ecdf`, `boxplot`, `violinplot`
2. **Two continuous variables**: `scatter`, `line`, `hexbin`
3. **Category comparison**: `bar`, `barh`, `boxplot`, `violinplot`
4. **Time series**: `line`, `fill_between`, `stackplot`
5. **2D field data**: `contour`, `contourf`, `pcolormesh`, `imshow`
6. **Statistical summary**: `stx_mean_ci`, `stx_mean_std`, `stx_median_iqr`
7. **Neuroscience**: `stx_raster`, `specgram`, `psd`, `cohere`

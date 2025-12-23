<!-- ---
!-- Timestamp: 2025-12-23 10:52:06
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_signatures/README.md
!-- --- -->

``` python
from figrecipe._signatures._loader import list_plotting_methods

print(list_plotting_methods())
# [
#  'acorr',
#  'angle_spectrum',
#  'bar',
#  'barbs',
#  'barh',
#  'boxplot',
#  'cohere',
#  'contour',
#  'contourf',
#  'csd',
#  'ecdf',
#  'errorbar',
#  'eventplot',
#  'fill',
#  'fill_between',
#  'fill_betweenx',
#  'hexbin',
#  'hist',
#  'hist2d',
#  'imshow',
#  'loglog',
#  'magnitude_spectrum',
#  'matshow',
#  'pcolor',
#  'pcolormesh',
#  'phase_spectrum',
#  'pie',
#  'plot',
#  'psd',
#  'quiver',
#  'scatter',
#  'semilogx',
#  'semilogy',
#  'specgram',
#  'spy',
#  'stackplot',
#  'stairs',
#  'stem',
#  'step',
#  'streamplot',
#  'tricontour',
#  'tricontourf',
#  'tripcolor',
#  'triplot',
#  'violinplot',
#  'xcorr'
# ]


from figrecipe._signatures._loader import get_signature
# Signature: get_signature(method_name: str) -> Dict[str, Any]

get_signature("plot")

```

<!-- EOF -->

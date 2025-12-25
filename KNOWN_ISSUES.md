<!-- ---
!-- Timestamp: 2025-12-25 07:04:17
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/KNOWN_ISSUES.md
!-- --- -->

## Partial color change
- [ ] Not working for some methods like ax.bar()
- [ ] Layout may shift after color update (needs more investigation - possibly related to constrained_layout handling)
- [x] Does not change color (e.g., in pie chart) - FIXED: _apply_colors_to_pie now respects custom colors

## Layout issues
- [ ] Blue rectangle artifact sometimes appears during updates (needs reproduction steps)

<!-- EOF -->

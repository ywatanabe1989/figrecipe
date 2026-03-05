/** Panel color palette — consistent colors across canvas, data table, and properties.
 *
 * Each panel (A, B, C...) gets a distinct color that visually links:
 * - Panel letter badge on canvas
 * - Data table tab
 * - Figure selection border
 * - Properties panel header
 */

const PANEL_COLORS = [
  "#4d96ff", // Blue   — Panel A
  "#ff6b6b", // Red    — Panel B
  "#6bcb77", // Green  — Panel C
  "#ffd93d", // Yellow — Panel D
  "#c77dff", // Purple — Panel E
  "#ff9f43", // Orange — Panel F
  "#48dbfb", // Cyan   — Panel G
  "#ff6b9d", // Pink   — Panel H
] as const;

/** Get panel color by index (0-based). Cycles if more than 8 panels. */
export function getPanelColor(index: number): string {
  return PANEL_COLORS[index % PANEL_COLORS.length];
}

/** Get panel color by letter (A=0, B=1, ...). Falls back to gray. */
export function getPanelColorByLetter(letter: string): string {
  if (!letter) return "#888888";
  const index = letter.charCodeAt(0) - 65; // 'A' = 0
  if (index < 0 || index > 25) return "#888888";
  return getPanelColor(index);
}

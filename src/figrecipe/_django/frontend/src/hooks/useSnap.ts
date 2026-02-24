/** Snap engine — axes-level, figure-edge, center, and grid snapping.
 *
 * Axes snap is the killer feature: aligns panels across figures so
 * data axes line up precisely for publication composition.
 *
 * Priority: axes > edge > center > grid (fallback).
 * Alt key bypasses all snapping for free movement.
 */

import type { PlacedFigure } from "../types/editor";

// ── Constants (A4 @ 300 DPI) ─────────────────────────────────
export const DPI = 300;
export const MM_PX = DPI / 25.4; // 11.811 px per mm
export const CANVAS_W = Math.round(210 * MM_PX); // 2480px
export const CANVAS_H = Math.round(297 * MM_PX); // 3508px

const SNAP_THRESHOLD = 10 * MM_PX; // ~118px hard snap distance (10mm)
const MAGNETIC_ZONE = 20 * MM_PX; // ~236px magnetic attraction zone (20mm)
const GRID_MM = 5; // 5mm grid

// ── Types ────────────────────────────────────────────────────
export interface SnapGuide {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  type: "axes" | "edge" | "center";
}

interface PanelBbox {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface SnapEdge {
  pos: number;
  type: "axes" | "edge" | "center";
  figTop: number;
  figBottom: number;
  figLeft: number;
  figRight: number;
}

// ── Helper: extract panel bboxes from figure's bboxes._meta ──
export function getPanelBboxes(fig: PlacedFigure): PanelBbox[] {
  const meta = (fig.bboxes as Record<string, unknown>)?._meta as
    | { panel_bboxes?: Record<string | number, PanelBbox> }
    | undefined;
  if (!meta?.panel_bboxes) return [];
  return Object.values(meta.panel_bboxes);
}

// ── Snap priority (lower = higher) ──────────────────────────
function snapPriority(type: "axes" | "edge" | "center"): number {
  switch (type) {
    case "axes":
      return 0;
    case "edge":
      return 1;
    case "center":
      return 2;
  }
}

// ── Find best snap match on one axis ────────────────────────
function findBestSnap(
  candidates: { pos: number; type: "axes" | "edge" | "center" }[],
  targets: SnapEdge[],
  threshold: number,
): {
  delta: number;
  type: "axes" | "edge" | "center";
  target: SnapEdge;
} | null {
  let bestDist = Infinity;
  let bestResult: {
    delta: number;
    type: "axes" | "edge" | "center";
    target: SnapEdge;
  } | null = null;

  for (const c of candidates) {
    for (const t of targets) {
      const dist = Math.abs(c.pos - t.pos);
      if (dist > MAGNETIC_ZONE) continue;

      // Determine snap type: axes if either side is axes
      const snapType: "axes" | "edge" | "center" =
        c.type === "axes" || t.type === "axes"
          ? "axes"
          : c.type === "center" && t.type === "center"
            ? "center"
            : "edge";

      const priority = snapPriority(snapType);
      const bestPriority = bestResult ? snapPriority(bestResult.type) : 999;

      // Prefer higher priority (lower number) when within 20% distance;
      // otherwise prefer closer distance
      if (
        dist < bestDist ||
        (dist < bestDist * 1.2 && priority < bestPriority)
      ) {
        bestDist = dist;

        // Hard lock within threshold; magnetic pull within zone
        let delta: number;
        if (dist <= threshold) {
          // Hard snap — lock to target
          delta = t.pos - c.pos;
        } else {
          // Magnetic zone — quadratic pull toward target
          const ratio = (dist - threshold) / (MAGNETIC_ZONE - threshold);
          const strength = 1 - ratio * ratio; // 1 at threshold edge, 0 at zone edge
          delta = (t.pos - c.pos) * strength;
        }

        bestResult = { delta, type: snapType, target: t };
      }
    }
  }

  return bestResult;
}

// ── Main snap function ──────────────────────────────────────
export function applySnapping(
  x: number,
  y: number,
  w: number,
  h: number,
  panelBboxes: PanelBbox[],
  otherFigures: PlacedFigure[],
  canvasW: number,
  canvasH: number,
  excludeIds?: string[],
): { x: number; y: number; guides: SnapGuide[] } {
  // Filter out group siblings so we don't snap to our own group
  if (excludeIds && excludeIds.length > 0) {
    const excludeSet = new Set(excludeIds);
    otherFigures = otherFigures.filter((f) => !excludeSet.has(f.id));
  }
  const guides: SnapGuide[] = [];

  // ── Collect targets ────────────────────────────────────────
  const xTargets: SnapEdge[] = [];
  const yTargets: SnapEdge[] = [];

  // Canvas edges and center
  const cb = { figTop: 0, figBottom: canvasH, figLeft: 0, figRight: canvasW };
  xTargets.push({ pos: 0, type: "edge", ...cb });
  xTargets.push({ pos: canvasW, type: "edge", ...cb });
  xTargets.push({ pos: canvasW / 2, type: "center", ...cb });
  yTargets.push({ pos: 0, type: "edge", ...cb });
  yTargets.push({ pos: canvasH, type: "edge", ...cb });
  yTargets.push({ pos: canvasH / 2, type: "center", ...cb });

  // Other figures
  for (const fig of otherFigures) {
    const ft = fig.y;
    const fb = fig.y + fig.imgSize.height;
    const fl = fig.x;
    const fr = fig.x + fig.imgSize.width;
    const bounds = { figTop: ft, figBottom: fb, figLeft: fl, figRight: fr };

    // Figure edges
    xTargets.push({ pos: fl, type: "edge", ...bounds });
    xTargets.push({ pos: fr, type: "edge", ...bounds });
    xTargets.push({ pos: (fl + fr) / 2, type: "center", ...bounds });
    yTargets.push({ pos: ft, type: "edge", ...bounds });
    yTargets.push({ pos: fb, type: "edge", ...bounds });
    yTargets.push({ pos: (ft + fb) / 2, type: "center", ...bounds });

    // Axes edges (killer feature)
    const otherPanels = getPanelBboxes(fig);
    for (const panel of otherPanels) {
      const axL = fig.x + panel.x;
      const axR = fig.x + panel.x + panel.width;
      const axT = fig.y + panel.y;
      const axB = fig.y + panel.y + panel.height;
      const axBounds = {
        figTop: axT,
        figBottom: axB,
        figLeft: axL,
        figRight: axR,
      };
      xTargets.push({ pos: axL, type: "axes", ...axBounds });
      xTargets.push({ pos: axR, type: "axes", ...axBounds });
      yTargets.push({ pos: axT, type: "axes", ...axBounds });
      yTargets.push({ pos: axB, type: "axes", ...axBounds });
    }
  }

  // ── Candidates from dragged figure ─────────────────────────
  const xCandidates: { pos: number; type: "axes" | "edge" | "center" }[] = [
    { pos: x, type: "edge" },
    { pos: x + w, type: "edge" },
    { pos: x + w / 2, type: "center" },
  ];
  for (const panel of panelBboxes) {
    xCandidates.push({ pos: x + panel.x, type: "axes" });
    xCandidates.push({ pos: x + panel.x + panel.width, type: "axes" });
  }

  const yCandidates: { pos: number; type: "axes" | "edge" | "center" }[] = [
    { pos: y, type: "edge" },
    { pos: y + h, type: "edge" },
    { pos: y + h / 2, type: "center" },
  ];
  for (const panel of panelBboxes) {
    yCandidates.push({ pos: y + panel.y, type: "axes" });
    yCandidates.push({ pos: y + panel.y + panel.height, type: "axes" });
  }

  // ── Find snaps ─────────────────────────────────────────────
  const xSnap = findBestSnap(xCandidates, xTargets, SNAP_THRESHOLD);
  const ySnap = findBestSnap(yCandidates, yTargets, SNAP_THRESHOLD);

  let snappedX = x;
  let snappedY = y;

  if (xSnap) {
    snappedX = x + xSnap.delta;
    const minY = Math.min(y, xSnap.target.figTop);
    const maxY = Math.max(y + h, xSnap.target.figBottom);
    guides.push({
      x1: xSnap.target.pos,
      y1: minY - 20,
      x2: xSnap.target.pos,
      y2: maxY + 20,
      type: xSnap.type,
    });
  } else {
    // Grid snap fallback
    const gridPx = GRID_MM * MM_PX;
    snappedX = Math.round(x / gridPx) * gridPx;
  }

  if (ySnap) {
    snappedY = y + ySnap.delta;
    const minX = Math.min(snappedX, ySnap.target.figLeft);
    const maxX = Math.max(snappedX + w, ySnap.target.figRight);
    guides.push({
      x1: minX - 20,
      y1: ySnap.target.pos,
      x2: maxX + 20,
      y2: ySnap.target.pos,
      type: ySnap.type,
    });
  } else {
    const gridPx = GRID_MM * MM_PX;
    snappedY = Math.round(y / gridPx) * gridPx;
  }

  return { x: snappedX, y: snappedY, guides };
}

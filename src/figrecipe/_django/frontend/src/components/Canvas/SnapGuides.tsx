/** SVG overlay for snap guide lines during drag.
 *
 * Colors by snap type:
 *   axes  — cyan (#00bcd4)  — the killer feature
 *   edge  — red (#ff6b6b)   — figure edge alignment
 *   center — purple (#a855f7) — center alignment
 */

import type { SnapGuide } from "../../hooks/useSnap";

const GUIDE_COLOR: Record<SnapGuide["type"], string> = {
  axes: "#00bcd4",
  edge: "#ff6b6b",
  center: "#a855f7",
  label: "#22c55e",
};

const GUIDE_WIDTH: Record<SnapGuide["type"], number> = {
  axes: 2,
  edge: 1.5,
  center: 1,
  label: 1,
};

const GUIDE_DASH: Record<SnapGuide["type"], string> = {
  axes: "none",
  edge: "none",
  center: "6 3",
  label: "4 3",
};

interface Props {
  guides: SnapGuide[];
  canvasWidth: number;
  canvasHeight: number;
}

export function SnapGuides({ guides, canvasWidth, canvasHeight }: Props) {
  if (guides.length === 0) return null;

  return (
    <svg
      className="snap-guides-overlay"
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: canvasWidth,
        height: canvasHeight,
        pointerEvents: "none",
        zIndex: 50,
        overflow: "visible",
      }}
      viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
    >
      {guides.map((g, i) => (
        <line
          key={i}
          x1={g.x1}
          y1={g.y1}
          x2={g.x2}
          y2={g.y2}
          stroke={GUIDE_COLOR[g.type]}
          strokeWidth={GUIDE_WIDTH[g.type]}
          strokeDasharray={GUIDE_DASH[g.type]}
          opacity={0.9}
        />
      ))}
    </svg>
  );
}

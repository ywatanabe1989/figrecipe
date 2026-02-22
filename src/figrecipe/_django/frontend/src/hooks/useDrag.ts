/** Reusable drag-to-move hook for canvas elements.
 *
 * Accounts for CSS transform scale (zoom) so the element tracks
 * the cursor precisely.  Alt key = free move (bypasses snapping + 10% speed).
 */

import { useCallback, useRef, useState } from "react";
import type { SnapGuide } from "./useSnap";

interface DragResult {
  isDragging: boolean;
  /** Offset in canvas-space pixels (already zoom-corrected) */
  dragOffset: { dx: number; dy: number };
  onMouseDown: (e: React.MouseEvent) => void;
}

export function useDrag(
  onDragEnd: (x: number, y: number) => void,
  startPos: { x: number; y: number },
  opts?: {
    /** Current canvas zoom (default 1). Screen deltas are divided by this. */
    zoom?: number;
    threshold?: number;
    onDragStart?: () => void;
    /** Snap function: receives raw absolute position, returns snapped position + guides */
    snapFn?: (
      x: number,
      y: number,
    ) => { x: number; y: number; guides: SnapGuide[] };
    /** Called during drag with current snap guides (empty = no snap active) */
    onSnapGuidesChange?: (guides: SnapGuide[]) => void;
  },
): DragResult {
  const threshold = opts?.threshold ?? 4;
  const zoom = opts?.zoom ?? 1;

  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ dx: 0, dy: 0 });

  const draggingRef = useRef(false);
  const originRef = useRef<{
    mx: number;
    my: number;
    fx: number;
    fy: number;
    zoom: number;
  } | null>(null);

  // Keep latest snap callbacks in refs to avoid stale closures
  const snapFnRef = useRef(opts?.snapFn);
  const guidesCallbackRef = useRef(opts?.onSnapGuidesChange);
  snapFnRef.current = opts?.snapFn;
  guidesCallbackRef.current = opts?.onSnapGuidesChange;

  const onMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button !== 0 || e.ctrlKey || e.metaKey) return;
      e.stopPropagation();

      originRef.current = {
        mx: e.clientX,
        my: e.clientY,
        fx: startPos.x,
        fy: startPos.y,
        zoom,
      };
      draggingRef.current = false;

      const handleMove = (ev: MouseEvent) => {
        if (!originRef.current) return;
        const z = originRef.current.zoom;

        // Screen pixels -> canvas pixels (divide by zoom)
        let dx = (ev.clientX - originRef.current.mx) / z;
        let dy = (ev.clientY - originRef.current.my) / z;

        // Alt = fine control (10% speed) + bypass snapping
        const altHeld = ev.altKey;
        if (altHeld) {
          dx *= 0.1;
          dy *= 0.1;
        }

        // Threshold in screen pixels
        const screenDist =
          Math.abs(ev.clientX - originRef.current.mx) +
          Math.abs(ev.clientY - originRef.current.my);
        if (!draggingRef.current && screenDist < threshold) return;

        if (!draggingRef.current) {
          draggingRef.current = true;
          setIsDragging(true);
          opts?.onDragStart?.();
        }

        // Apply snapping to absolute position (unless Alt held)
        if (snapFnRef.current && !altHeld) {
          const rawX = Math.max(0, originRef.current.fx + dx);
          const rawY = Math.max(0, originRef.current.fy + dy);
          const snapped = snapFnRef.current(rawX, rawY);
          dx = snapped.x - originRef.current.fx;
          dy = snapped.y - originRef.current.fy;
          guidesCallbackRef.current?.(snapped.guides);
        } else {
          guidesCallbackRef.current?.([]);
        }

        setDragOffset({ dx, dy });
      };

      const handleUp = (ev: MouseEvent) => {
        document.removeEventListener("mousemove", handleMove);
        document.removeEventListener("mouseup", handleUp);
        document.body.style.cursor = "";

        if (draggingRef.current && originRef.current) {
          const z = originRef.current.zoom;
          let dx = (ev.clientX - originRef.current.mx) / z;
          let dy = (ev.clientY - originRef.current.my) / z;

          const altHeld = ev.altKey;
          if (altHeld) {
            dx *= 0.1;
            dy *= 0.1;
          }

          let finalX = Math.max(0, originRef.current.fx + dx);
          let finalY = Math.max(0, originRef.current.fy + dy);

          // Apply snap to final position
          if (snapFnRef.current && !altHeld) {
            const snapped = snapFnRef.current(finalX, finalY);
            finalX = snapped.x;
            finalY = snapped.y;
          }

          onDragEnd(finalX, finalY);
        }

        // Clear guides
        guidesCallbackRef.current?.([]);

        originRef.current = null;
        draggingRef.current = false;
        setIsDragging(false);
        setDragOffset({ dx: 0, dy: 0 });
      };

      document.addEventListener("mousemove", handleMove);
      document.addEventListener("mouseup", handleUp);
      document.body.style.cursor = "move";
    },
    [startPos.x, startPos.y, zoom, threshold, onDragEnd, opts],
  );

  return { isDragging, dragOffset, onMouseDown };
}

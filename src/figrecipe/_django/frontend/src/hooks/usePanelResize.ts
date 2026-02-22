/**
 * Panel resize + collapse hook — React port of vis_app WorkspacePanelResizer.
 *
 * Features:
 * - Drag resize via mousedown on resizer element
 * - Auto-collapse when dragged to minWidth
 * - Double-click header to toggle collapse
 * - Drag from collapsed state auto-expands
 * - localStorage persistence for width + collapsed state
 */

import { useCallback, useEffect, useRef, useState } from "react";

export interface PanelResizeConfig {
  direction: "left" | "right";
  minWidth: number;
  defaultWidth: number;
  storageKey: string;
  collapseKey: string;
}

export interface PanelResizeResult {
  width: number;
  collapsed: boolean;
  resizerProps: {
    onMouseDown: (e: React.MouseEvent) => void;
  };
  headerProps: {
    onDoubleClick: () => void;
    "data-tooltip": string;
  };
  toggleCollapse: () => void;
}

function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* quota exceeded — ignore */
  }
}

export function usePanelResize(config: PanelResizeConfig): PanelResizeResult {
  const { direction, minWidth, defaultWidth, storageKey, collapseKey } = config;

  // Restore initial state from localStorage
  const [width, setWidth] = useState(() => {
    const saved = readStorage(storageKey);
    if (saved) {
      const w = parseInt(saved, 10);
      if (w >= minWidth) return w;
    }
    return defaultWidth;
  });

  const [collapsed, setCollapsed] = useState(() => {
    return readStorage(collapseKey) === "true";
  });

  // Refs for drag state (avoid re-renders during drag)
  const dragging = useRef(false);
  const startX = useRef(0);
  const startWidth = useRef(0);
  const wasCollapsed = useRef(false);

  // Persist width changes
  const saveWidth = useCallback(
    (w: number) => {
      writeStorage(storageKey, w.toString());
    },
    [storageKey],
  );

  // Persist collapse state
  const saveCollapsed = useCallback(
    (c: boolean) => {
      writeStorage(collapseKey, c.toString());
    },
    [collapseKey],
  );

  // Toggle collapse/expand
  const toggleCollapse = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      saveCollapsed(next);
      if (!next) {
        // Expanding: restore saved width
        const saved = readStorage(storageKey);
        if (saved) {
          const w = parseInt(saved, 10);
          if (w > minWidth + 10) {
            setWidth(w);
            return next;
          }
        }
        setWidth(defaultWidth);
      }
      return next;
    });
  }, [saveCollapsed, storageKey, minWidth, defaultWidth]);

  // Mouse handlers for drag resize
  const onMouseDown = useCallback(
    (e: React.MouseEvent) => {
      wasCollapsed.current = collapsed;

      // If collapsed, auto-expand first
      if (collapsed) {
        setCollapsed(false);
        saveCollapsed(false);
        setWidth(minWidth);
      }

      dragging.current = true;
      startX.current = e.clientX;
      startWidth.current = collapsed ? minWidth : width;

      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
      e.preventDefault();
    },
    [collapsed, width, minWidth, saveCollapsed],
  );

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const delta = e.clientX - startX.current;
      const newWidth =
        direction === "left"
          ? startWidth.current + delta
          : startWidth.current - delta;
      if (newWidth >= minWidth) {
        setWidth(newWidth);
      }
    };

    const onMouseUp = () => {
      if (!dragging.current) return;
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";

      // Read current width from state via closure-safe ref pattern
      setWidth((current) => {
        if (current <= minWidth + 10) {
          // Auto-collapse
          setCollapsed(true);
          saveCollapsed(true);
          return defaultWidth; // store the default for next expand
        }
        saveWidth(current);
        return current;
      });

      wasCollapsed.current = false;
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    return () => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, [direction, minWidth, defaultWidth, saveWidth, saveCollapsed]);

  return {
    width,
    collapsed,
    resizerProps: { onMouseDown },
    headerProps: {
      onDoubleClick: toggleCollapse,
      "data-tooltip": collapsed
        ? "Double-click to expand"
        : "Double-click to collapse",
    },
    toggleCollapse,
  };
}

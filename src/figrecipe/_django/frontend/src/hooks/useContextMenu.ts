/** Context menu state — position, visibility, and target figure. */

import { useCallback, useEffect, useState } from "react";

interface ContextMenuState {
  visible: boolean;
  x: number;
  y: number;
  figureId: string | null;
}

export function useContextMenu() {
  const [menu, setMenu] = useState<ContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    figureId: null,
  });

  const show = useCallback((e: React.MouseEvent, figureId: string | null) => {
    e.preventDefault();
    e.stopPropagation();
    setMenu({ visible: true, x: e.clientX, y: e.clientY, figureId });
  }, []);

  const hide = useCallback(() => {
    setMenu((m) => (m.visible ? { ...m, visible: false } : m));
  }, []);

  // Close on click outside or Escape
  useEffect(() => {
    if (!menu.visible) return;

    const handleClick = () => hide();
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") hide();
    };

    // Delay to avoid closing immediately on the same click
    const timer = setTimeout(() => {
      document.addEventListener("mousedown", handleClick);
      document.addEventListener("keydown", handleKey);
    }, 0);

    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKey);
    };
  }, [menu.visible, hide]);

  return { menu, show, hide };
}

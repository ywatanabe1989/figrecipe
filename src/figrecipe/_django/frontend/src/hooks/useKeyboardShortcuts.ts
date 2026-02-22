/** Global keyboard shortcuts — extracted from Toolbar.tsx. */

import { useEffect } from "react";
import { useEditorStore } from "../store/useEditorStore";

export function useKeyboardShortcuts() {
  const save = useEditorStore((s) => s.save);
  const restore = useEditorStore((s) => s.restore);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;

      if (mod && e.key === "s") {
        e.preventDefault();
        save();
        return;
      }

      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        restore();
        return;
      }

      if (e.key === "Escape") {
        useEditorStore.getState().selectElement(null);
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [save, restore]);
}

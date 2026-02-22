/** Global keyboard shortcuts. */

import { useEffect } from "react";
import { useEditorStore } from "../store/useEditorStore";

export function useKeyboardShortcuts() {
  const save = useEditorStore((s) => s.save);
  const restore = useEditorStore((s) => s.restore);
  const selectedFigureId = useEditorStore((s) => s.selectedFigureId);
  const removeFigure = useEditorStore((s) => s.removeFigure);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;
      const tag = (e.target as HTMLElement).tagName;
      const isEditing =
        tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";

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
        useEditorStore.getState().selectFigure(null);
        useEditorStore.getState().selectElement(null);
        return;
      }

      // Delete/Backspace → remove selected figure (skip when typing)
      if ((e.key === "Delete" || e.key === "Backspace") && !isEditing) {
        if (selectedFigureId) {
          e.preventDefault();
          removeFigure(selectedFigureId);
        }
      }

      // Ctrl+G → group all figures
      if (mod && e.key === "g" && !e.shiftKey) {
        e.preventDefault();
        const state = useEditorStore.getState();
        const ids = state.placedFigures.map((f) => f.id);
        if (ids.length >= 2) state.groupFigures(ids);
        return;
      }

      // Ctrl+Shift+G → ungroup selected figure
      if (mod && e.key === "G" && e.shiftKey) {
        e.preventDefault();
        const state = useEditorStore.getState();
        const sel = state.placedFigures.find(
          (f) => f.id === state.selectedFigureId,
        );
        if (sel?.groupId) state.ungroupFigures(sel.groupId);
        return;
      }

      // Ctrl+Shift+S → toggle snap
      if (mod && e.key === "S" && e.shiftKey) {
        e.preventDefault();
        useEditorStore.getState().toggleSnap();
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [save, restore, selectedFigureId, removeFigure]);
}

/** Global keyboard shortcuts. */

import { useEffect } from "react";
import { MM_PX } from "./useSnap";
import { useEditorStore } from "../store/useEditorStore";
import { redo, undo } from "./useUndoRedo";

const NUDGE_MM = 1; // 1mm per arrow press
const NUDGE_SHIFT_MM = 5; // 5mm with Shift held

export function useKeyboardShortcuts() {
  const save = useEditorStore((s) => s.save);
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

      // Ctrl+Z → undo
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        undo();
        return;
      }

      // Ctrl+Shift+Z → redo
      if (mod && e.key === "Z" && e.shiftKey) {
        e.preventDefault();
        redo();
        return;
      }

      // Ctrl+C → copy
      if (mod && e.key === "c" && !isEditing) {
        e.preventDefault();
        useEditorStore.getState().copyFigure();
        return;
      }

      // Ctrl+V → paste
      if (mod && e.key === "v" && !isEditing) {
        e.preventDefault();
        useEditorStore.getState().pasteFigure();
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
        return;
      }

      // Arrow keys → nudge selected figure
      if (
        ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key) &&
        !isEditing &&
        !mod
      ) {
        const state = useEditorStore.getState();
        const fig = state.placedFigures.find(
          (f) => f.id === state.selectedFigureId,
        );
        if (!fig) return;

        e.preventDefault();
        const px = (e.shiftKey ? NUDGE_SHIFT_MM : NUDGE_MM) * MM_PX;
        let dx = 0;
        let dy = 0;
        if (e.key === "ArrowLeft") dx = -px;
        if (e.key === "ArrowRight") dx = px;
        if (e.key === "ArrowUp") dy = -px;
        if (e.key === "ArrowDown") dy = px;
        state.moveFigure(fig.id, fig.x + dx, fig.y + dy);
        return;
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
  }, [save, selectedFigureId, removeFigure]);
}

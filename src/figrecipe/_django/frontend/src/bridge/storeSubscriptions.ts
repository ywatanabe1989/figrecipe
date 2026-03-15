/** Store subscriptions: Zustand state changes → scitex-ui component updates. */

import type { FileBrowser } from "scitex-ui/ts/app/file-browser";
import type { StatusBar } from "scitex-ui/ts/shell/status-bar";
import type { FileNode } from "scitex-ui/ts/app/file-browser/types";
import { useEditorStore } from "../store/useEditorStore";
import type { FileTreeItem } from "../types/editor";

/** Convert figrecipe FileTreeItem[] to scitex-ui FileNode[]. */
function toFileNodes(items: FileTreeItem[]): FileNode[] {
  return items.map((item) => ({
    name: item.name,
    path: item.path,
    type: item.type,
    has_image: item.has_image,
    is_current: item.is_current,
    children: item.children ? toFileNodes(item.children) : undefined,
  }));
}

/** Subscribe to Zustand store and push updates to scitex-ui StatusBar. */
export function subscribeStatusBar(statusBar: StatusBar): () => void {
  return useEditorStore.subscribe((state, prev) => {
    // Figure count
    if (state.placedFigures.length !== prev.placedFigures.length) {
      const n = state.placedFigures.length;
      statusBar.updateItem("figures", {
        text: `${n} figure${n !== 1 ? "s" : ""}`,
      });
    }

    // Figure size
    if (state.figSizeMm !== prev.figSizeMm && state.figSizeMm) {
      statusBar.updateItem("size", {
        text: `${state.figSizeMm.width.toFixed(0)} x ${state.figSizeMm.height.toFixed(0)} mm`,
      });
    }

    // Selection info
    if (state.selectedFigureId !== prev.selectedFigureId) {
      const fig = state.placedFigures.find(
        (f) => f.id === state.selectedFigureId,
      );
      statusBar.updateItem("selection", {
        text: fig ? (fig.path.split("/").pop() ?? "Selected") : "No selection",
      });
    }

    // Snap toggle
    if (state.snapEnabled !== prev.snapEnabled) {
      statusBar.updateItem("snap", {
        text: `Snap ${state.snapEnabled ? "on" : "off"}`,
      });
    }

    // Ruler toggle
    if (
      state.showRulers !== prev.showRulers ||
      state.rulerUnit !== prev.rulerUnit
    ) {
      statusBar.updateItem("rulers", {
        text: state.showRulers ? state.rulerUnit : "Rulers off",
      });
    }
  });
}

/** Subscribe to Zustand store and push updates to scitex-ui FileBrowser. */
export function subscribeFileBrowser(fileBrowser: FileBrowser): () => void {
  return useEditorStore.subscribe((state, prev) => {
    // File list changed
    if (state.files !== prev.files) {
      fileBrowser.setData(toFileNodes(state.files));
    }

    // Current file changed
    if (state.currentFile !== prev.currentFile && state.currentFile) {
      fileBrowser.select(state.currentFile);
    }
  });
}

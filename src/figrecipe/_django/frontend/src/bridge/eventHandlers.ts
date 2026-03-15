/** Event handlers: scitex-ui vanilla TS callbacks → Zustand store updates. */

import type { FileNode } from "scitex-ui/ts/app/file-browser/types";
import type { Theme } from "scitex-ui/ts/shell/theme-provider/types";
import { useEditorStore } from "../store/useEditorStore";

/** Called by scitex-ui FileBrowser when a file is clicked. */
export function onFileSelect(node: FileNode): void {
  if (node.type === "file") {
    useEditorStore.getState().switchFile(node.path);
  }
}

/** Called by scitex-ui ThemeProvider when theme changes. */
export function onThemeChange(theme: Theme): void {
  useEditorStore.getState().setDarkMode(theme === "dark");
}

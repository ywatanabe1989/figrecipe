/** FigrecipeEditor — mountable wrapper with event callback props.
 *
 * This is the public API for embedding figrecipe's React editor into
 * external applications (e.g. scitex-cloud) without an iframe.
 *
 * Usage:
 *   import { FigrecipeEditor } from "figrecipe-editor";
 *   <FigrecipeEditor
 *     apiBaseUrl="/vis/api/figrecipe"
 *     workingDir="/path/to/project"
 *     onFileSelect={(path) => console.log("file:", path)}
 *   />
 */

import { useEffect, useMemo } from "react";
import { App } from "./App";
import { useEditorStore } from "./store/useEditorStore";
import type { BBox, StatBracket } from "./types/editor";

export interface FigrecipeEditorProps {
  /** Base URL for the figrecipe API (e.g. "/vis/api/figrecipe"). */
  apiBaseUrl?: string;
  /** Project working directory (injected server-side). */
  workingDir?: string;
  /** Initial recipe path to load. */
  recipe?: string;
  /** Dark mode. */
  darkMode?: boolean;
  /** Called when a file is selected in the file tree. */
  onFileSelect?: (path: string) => void;
  /** Called when an element is clicked on the canvas. */
  onElementSelect?: (elementId: string, bbox: BBox | null) => void;
  /** Called when a property is changed. */
  onPropertyChange?: (key: string, value: unknown) => void;
  /** Called when data is imported/changed. */
  onDataChange?: (columns: string[], rowCount: number) => void;
  /** Called when a stat bracket is added. */
  onStatBracketAdd?: (bracket: StatBracket) => void;
}

export function FigrecipeEditor({
  apiBaseUrl,
  workingDir,
  recipe,
  darkMode,
  onFileSelect,
  onElementSelect,
}: FigrecipeEditorProps) {
  // Set API base URL via query params if provided
  useMemo(() => {
    if (apiBaseUrl || workingDir || recipe) {
      const params = new URLSearchParams(window.location.search);
      if (recipe) params.set("recipe", recipe);
      if (workingDir) params.set("working_dir", workingDir);
      // Mode=embedded hides file tree + status bar
      params.set("mode", "embedded");
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState(null, "", newUrl);
    }
  }, [apiBaseUrl, workingDir, recipe]);

  // Subscribe to store changes and forward as callbacks
  useEffect(() => {
    if (!onFileSelect && !onElementSelect) return;

    const unsub = useEditorStore.subscribe((state, prevState) => {
      if (onFileSelect && state.currentFile !== prevState.currentFile) {
        if (state.currentFile) onFileSelect(state.currentFile);
      }
      if (
        onElementSelect &&
        state.selectedElement !== prevState.selectedElement
      ) {
        if (state.selectedElement) {
          onElementSelect(state.selectedElement, state.selectedBbox);
        }
      }
    });

    return unsub;
  }, [onFileSelect, onElementSelect]);

  // Apply dark mode prop
  useEffect(() => {
    if (darkMode !== undefined) {
      useEditorStore.getState().setDarkMode(darkMode);
    }
  }, [darkMode]);

  return <App />;
}

// Re-export types for consumers
export type { BBox, StatBracket, CallRecord } from "./types/editor";
export { useEditorStore } from "./store/useEditorStore";

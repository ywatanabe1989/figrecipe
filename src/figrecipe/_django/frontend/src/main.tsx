/** FigRecipe Editor — Bootstrap.
 *
 * The workspace shell (Console/Chat | Files | Viewer | App) is provided by
 * scitex-ui's vanilla TS system via the Django standalone_shell.html template.
 * This file only mounts the React InnerEditor into the app content area (#root).
 *
 * Shell features (file tree, terminal, chat, toolbar) are ALL vanilla TS from scitex-ui.
 * React is ONLY used for the app content (DataTable, Canvas, Properties panels).
 */

import React from "react";
import ReactDOM from "react-dom/client";

// React app content (Plot/Canvas editor — NOT shell)
import { InnerEditor } from "./InnerEditor";

// Styles (app-specific)
import "./styles/app-variables.css";
import "./styles/layout.css";
import "./styles/context-menu.css";
import "./styles/canvas.css";
import "./styles/panels.css";
import "./styles/gallery.css";
import "./styles/export-dialog.css";
import "./styles/feedback.css";

// scitex-ui CSS — single bundle import (shell + app + utils)
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/css/all.css";

// Element inspector — debug overlay (Alt+I to toggle)
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/utils/element-inspector";

// Context-aware zoom — app-specific panes only (shell panes use vanilla TS zoom)
import { bootstrapContextZoom } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/utils/context-zoom";

// Vanilla TS workspace shell — panel resizer initialization
import "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/workspace-panel-resizer";

// Vanilla TS standalone terminal — xterm.js + WebSocket to local PTY
import "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/standalone-terminal";

// Vanilla TS shell file tree — adapter-based, with hidden files toggle
import { ShellFileTree } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/file-tree";
import type { FileTreeAdapter } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/file-tree";

// Vanilla TS shell toolbar + keyboard shortcuts
import {
  ToolbarManager,
  KeyboardShortcuts,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/toolbar";

// Mount React InnerEditor into app content area ONLY
const root = document.getElementById("root");
const params = new URLSearchParams(window.location.search);
const embedded = params.get("mode") === "embedded";

if (root) {
  document.documentElement.setAttribute("data-theme", "dark");
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <InnerEditor embedded={embedded} />
    </React.StrictMode>,
  );
}

// Shell file tree — connects to figrecipe's api/tree endpoint
const figrecipeFileTreeAdapter: FileTreeAdapter = {
  async fetchTree() {
    const resp = await fetch("api/tree");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
    const data = await resp.json();
    return data.tree ?? [];
  },
};

const shellFileTree = new ShellFileTree({
  container: "#ws-worktree-tree",
  adapter: figrecipeFileTreeAdapter,
  onFileSelect: (node) => {
    // Dispatch event for the React app to handle file selection
    window.dispatchEvent(
      new CustomEvent("figrecipe:file-select", {
        detail: { path: node.path, name: node.name },
      }),
    );
  },
});
shellFileTree.load();

// Wire hidden files toggle button if it exists in shell template
const hiddenToggle = document.getElementById("hidden-files-toggle");
if (hiddenToggle) {
  hiddenToggle.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    shellFileTree.toggleHidden();
  });
}

// Shell toolbar + keyboard shortcuts
const toolbar = new ToolbarManager();
toolbar.init();
const shortcuts = new KeyboardShortcuts();
shortcuts.init();

// Register zoom on app-specific panes
bootstrapContextZoom(
  [
    {
      selector: ".split-pane-left",
      storageKey: "figrecipe-table-zoom",
      min: 0.7,
      max: 1.6,
    },
    {
      selector: ".split-pane-center",
      storageKey: "figrecipe-center-zoom",
      min: 0.7,
      max: 1.6,
    },
    {
      selector: ".split-pane-right",
      storageKey: "figrecipe-props-zoom",
      min: 0.7,
      max: 1.6,
    },
  ],
  [],
);

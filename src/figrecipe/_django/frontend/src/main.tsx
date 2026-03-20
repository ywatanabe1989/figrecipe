/** FigRecipe Editor — Bootstrap.
 *
 * The workspace shell (Console/Chat | Files | Viewer | App) is provided by
 * scitex-ui's vanilla TS system via the Django standalone_shell.html template.
 * This file only mounts the React InnerEditor into the app content area.
 *
 * The React Workspace wrapper has been archived — see GITIGNORED/archive/
 */

import React from "react";
import ReactDOM from "react-dom/client";

// React app content
import { InnerEditor } from "./InnerEditor";

// Styles
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

// Context-aware zoom — app-specific panes only
import { bootstrapContextZoom } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/utils/context-zoom";

// Vanilla TS workspace shell — panel resizer initialization
// This auto-discovers [data-panel-resizer] elements and sets up drag resize
import "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/workspace-panel-resizer";

// Vanilla TS standalone terminal — xterm.js + WebSocket to local PTY
import "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/standalone-terminal";

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

// Register zoom on app-specific panes (shell panes use vanilla TS zoom)
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

/** FigRecipe Editor — Bootstrap.
 *
 * Initializes scitex-ui shell components (ThemeProvider, AppShell, StatusBar,
 * FileBrowser), then mounts the React editor into the AppShell's mainContent slot.
 *
 * In embedded mode (?mode=embedded), skips the shell and mounts React directly.
 */

import React from "react";
import ReactDOM from "react-dom/client";

// scitex-ui shell components (bundled at build time)
import { ThemeProvider } from "scitex-ui/ts/shell/theme-provider";
import { AppShell } from "scitex-ui/ts/shell/app-shell";
import { StatusBar } from "scitex-ui/ts/shell/status-bar";
import { FileBrowser } from "scitex-ui/ts/app/file-browser";

// Bridge: scitex-ui ↔ React
import { onFileSelect, onThemeChange } from "./bridge/eventHandlers";
import {
  subscribeStatusBar,
  subscribeFileBrowser,
} from "./bridge/storeSubscriptions";

// React app
import { InnerEditor } from "./InnerEditor";

// Styles: scitex-ui theme + app-specific variables
import "scitex-ui/css/shell/theme.css";
import "scitex-ui/css/shell/app-shell.css";
import "scitex-ui/css/shell/status-bar.css";
import "scitex-ui/css/app/file-browser.css";
import "./styles/app-variables.css";
import "./styles/layout.css";
import "./styles/context-menu.css";
import "./styles/canvas.css";
import "./styles/panels.css";
import "./styles/gallery.css";
import "./styles/export-dialog.css";
import "./styles/feedback.css";

const root = document.getElementById("root")!;
const embedded =
  new URLSearchParams(window.location.search).get("mode") === "embedded";

if (embedded) {
  // Embedded mode: no shell, mount React directly
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <InnerEditor embedded />
    </React.StrictMode>,
  );
} else {
  // Standalone mode: scitex-ui shell wraps React editor

  // 1. Theme provider (light/dark, persisted to localStorage)
  const themeProvider = new ThemeProvider({
    defaultTheme: "dark",
    onThemeChange,
  });

  // 2. AppShell (sidebar + main content)
  const shell = new AppShell({
    container: root,
    sidebarTitle: "Files",
    sidebarIcon: "fas fa-folder-open",
    sidebarWidth: 200,
    accent: "figrecipe",
    storageKey: "figrecipe-sidebar-state",
  });

  // 3. File toolbar (React, mounted in sidebar above FileBrowser)
  const toolbarMount = document.createElement("div");
  shell.sidebarContent.appendChild(toolbarMount);

  // Lazy import to avoid circular deps
  import("./components/FileTreeToolbar").then(({ FileTreeToolbar }) => {
    ReactDOM.createRoot(toolbarMount).render(
      <React.StrictMode>
        <FileTreeToolbar />
      </React.StrictMode>,
    );
  });

  // 4. FileBrowser (scitex-ui vanilla TS, in sidebar below toolbar)
  const fileBrowserMount = document.createElement("div");
  fileBrowserMount.style.flex = "1";
  fileBrowserMount.style.overflow = "auto";
  shell.sidebarContent.appendChild(fileBrowserMount);

  const fileBrowser = new FileBrowser({
    container: fileBrowserMount,
    onFileSelect,
    showImageBadge: true,
  });

  // 5. StatusBar (scitex-ui vanilla TS, after shell)
  const statusBarMount = document.createElement("div");
  root.appendChild(statusBarMount);

  const statusBar = new StatusBar({
    container: statusBarMount,
    showThemeToggle: true,
    items: {
      left: [
        { id: "figures", text: "0 figures", icon: "fas fa-images" },
        { id: "size", text: "" },
      ],
      center: [{ id: "selection", text: "No selection" }],
      right: [
        { id: "snap", text: "Snap on", icon: "fas fa-magnet" },
        { id: "rulers", text: "mm", icon: "fas fa-ruler" },
      ],
    },
  });

  // 6. Mount React editor into AppShell's main content slot
  ReactDOM.createRoot(shell.mainContent).render(
    <React.StrictMode>
      <InnerEditor />
    </React.StrictMode>,
  );

  // 7. Wire up Zustand → scitex-ui subscriptions
  subscribeStatusBar(statusBar);
  subscribeFileBrowser(fileBrowser);

  // Keep references alive for HMR cleanup
  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      themeProvider.destroy();
      fileBrowser.destroy();
      statusBar.destroy();
      shell.destroy();
    });
  }
}

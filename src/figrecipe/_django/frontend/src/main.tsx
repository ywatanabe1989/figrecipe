/** FigRecipe Editor — Bootstrap with Workspace Shell.
 *
 * Uses scitex-ui's React Workspace shell for the universal frame:
 * AI Chat (left) | File Tree (middle) | App Content (right) | Terminal (bottom)
 *
 * In embedded mode (?mode=embedded), skips the shell and mounts React directly.
 */

import React, { useMemo } from "react";
import ReactDOM from "react-dom/client";

// scitex-ui React workspace shell
import { Workspace } from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/shell/workspace";
import { LocalTerminalBackend } from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/shell/terminal/backends/LocalTerminalBackend";
import type {
  FileTreeBackend,
  FileNode,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/shell/workspace/types";

// React app content
import { InnerEditor } from "./InnerEditor";
import { api } from "./api/client";
import { useEditorStore } from "./store/useEditorStore";

// Styles
import "./styles/app-variables.css";
import "./styles/layout.css";
import "./styles/context-menu.css";
import "./styles/canvas.css";
import "./styles/panels.css";
import "./styles/gallery.css";
import "./styles/export-dialog.css";
import "./styles/feedback.css";

// scitex-ui CSS (shared with vanilla TS components)
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/css/shell/theme.css";
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/css/shell/workspace.css";
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/css/shell/terminal.css";
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/css/shell/chat.css";
// @ts-ignore
import "@scitex/ui/src/scitex_ui/static/scitex_ui/css/app/file-browser.css";

const root = document.getElementById("root")!;
const params = new URLSearchParams(window.location.search);
const embedded = params.get("mode") === "embedded";

/** File tree backend using figrecipe's existing API */
class FigrecipeFileTreeBackend implements FileTreeBackend {
  async fetchTree(): Promise<FileNode[]> {
    const data = await api.get<{ tree: FileNode[] }>("api/files");
    return data.tree || [];
  }
}

function FigrecipeApp() {
  const { switchFile } = useEditorStore();

  // Terminal backend — connects to pty server on port+1
  const terminalBackend = useMemo(() => {
    const port = parseInt(window.location.port || "5050", 10);
    return new LocalTerminalBackend(`ws://127.0.0.1:${port + 1}/`);
  }, []);

  // File tree backend — uses figrecipe's API
  const fileTreeBackend = useMemo(() => new FigrecipeFileTreeBackend(), []);

  return (
    <Workspace
      appName="figrecipe"
      accentColor="#7c5cbf"
      terminalBackend={terminalBackend}
      fileTreeBackend={fileTreeBackend}
      highlightExtensions={[".yaml", ".yml"]}
      onFileSelect={(node) => {
        if (node.path.endsWith(".yaml") || node.path.endsWith(".yml")) {
          switchFile(node.path);
        }
      }}
      onFileDrop={(path) => {
        if (path.endsWith(".csv") || path.endsWith(".tsv")) {
          // TODO: load into data table
        }
      }}
    >
      <InnerEditor />
    </Workspace>
  );
}

if (embedded) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <InnerEditor embedded />
    </React.StrictMode>,
  );
} else {
  // Apply dark theme by default
  document.documentElement.setAttribute("data-theme", "dark");

  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <FigrecipeApp />
    </React.StrictMode>,
  );
}

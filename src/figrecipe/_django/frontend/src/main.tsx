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

// Vanilla TS shell terminal — unified factory with adapter pattern
import { initTerminal } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/terminal";
import type { TerminalConnectionAdapter } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/terminal";

// Vanilla TS shell file tree — adapter-based, with hidden files toggle
import { ShellFileTree } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/file-tree";
import type { FileTreeAdapter } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/file-tree";

// Vanilla TS shell toolbar + keyboard shortcuts
import {
  ToolbarManager,
  KeyboardShortcuts,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/toolbar";

// Vanilla TS shell keyboard shortcuts + modal (Alt+A, Alt+T, pane cycling)
import {
  initKeyboardShortcuts,
  registerShortcuts,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/keyboard-shortcuts";

// Vanilla TS shell viewer — file viewing (images, PDFs, text)
import { ViewerManager } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/viewer";
import type { ViewerAdapter } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/viewer";

// Vanilla TS shell chat media — webcam, sketch, image input (from scitex-ui)
import { ImageInputManager } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat/_image-input";
import { WebcamCapture } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat/_webcam-capture";
import { SketchCanvas } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat/_sketch-canvas";
import { VoiceRecorder } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat/_recorder";
// ConfigMode class available but not needed — popover is in template HTML

// Chat wiring — SSE streaming to figrecipe's api/chat/stream endpoint
import { initChatWiring } from "./chat-wiring";

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

// Shell terminal — local PTY via WebSocket on port+1
const figrecipeTerminalAdapter: TerminalConnectionAdapter = {
  getWebSocketUrl() {
    const port = parseInt(window.location.port || "5050", 10);
    return `ws://127.0.0.1:${port + 1}/`;
  },
};
initTerminal({
  container: "#stx-shell-ai-console-terminal",
  adapter: figrecipeTerminalAdapter,
  clipboard: true,
});

// Shell toolbar + keyboard shortcuts
const toolbar = new ToolbarManager();
toolbar.init();
const shortcuts = new KeyboardShortcuts();
shortcuts.init();

// Shell keyboard shortcuts — Alt+A (toggle AI), Alt+T (cycle panes), etc.
initKeyboardShortcuts();
// Register figrecipe-specific shortcuts for the modal
registerShortcuts("figrecipe", [
  {
    title: "Figure Editor",
    shortcuts: [
      { keys: "Ctrl+Z", description: "Undo" },
      { keys: "Ctrl+Y", description: "Redo" },
      { keys: "Del", description: "Delete selected" },
    ],
  },
]);

// Shell viewer — opens files from file tree in the viewer pane
const figrecipeViewerAdapter: ViewerAdapter = {
  async readFile(path: string) {
    const resp = await fetch(`api/file-content/${path}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    return { content: data.content ?? "" };
  },
  getFileUrl(path: string) {
    return `api/file-content/${path}?raw=true`;
  },
};

let shellViewer: ViewerManager | null = null;
try {
  shellViewer = new ViewerManager({
    adapter: figrecipeViewerAdapter,
  });
} catch {
  // Viewer pane may not exist
}

// Wire file tree → viewer: double-clicking opens files in viewer
window.addEventListener("figrecipe:file-select", ((e: CustomEvent) => {
  if (shellViewer && e.detail?.path) {
    shellViewer.openFile(e.detail.path);
  }
}) as EventListener);

// Wire toolbar media buttons (camera, sketch, mic) — scitex-ui UI components
// Image input manager for chat attachments
const chatPreview = document.getElementById("stx-shell-ai-image-preview");
const chatFileInput = document.getElementById(
  "stx-shell-ai-file-input",
) as HTMLInputElement | null;
let imageInput: ImageInputManager | null = null;
let webcamCapture: WebcamCapture | null = null;
let sketchCanvas: SketchCanvas | null = null;
let voiceRecorder: VoiceRecorder | null = null;

if (chatPreview && chatFileInput) {
  imageInput = new ImageInputManager(chatPreview, chatFileInput);
  webcamCapture = new WebcamCapture(imageInput, chatFileInput);
  sketchCanvas = new SketchCanvas(imageInput);

  // Voice recorder — volume bars from DOM
  const volBars = Array.from(
    document.querySelectorAll<HTMLElement>(".stx-shell-ai-vol-bar"),
  );
  const micBtn = document.querySelector<HTMLButtonElement>(
    '.stx-shell-ai-input-btn[title="Voice"]',
  );
  voiceRecorder = new VoiceRecorder(volBars, micBtn);

  // Bind clipboard paste on chat textarea
  const chatTextarea = document.getElementById(
    "stx-shell-ai-input",
  ) as HTMLTextAreaElement | null;
  if (chatTextarea) {
    imageInput.bindPaste(chatTextarea);
  }
}

// Initialize chat wiring — connects textarea to SSE backend + markdown rendering
initChatWiring({ imageInput });

// Camera button → open webcam capture (scitex-ui WebcamCapture)
window.addEventListener("stx-shell:camera", () => {
  if (webcamCapture) {
    webcamCapture.open();
  } else if (chatFileInput) {
    chatFileInput.click();
  }
});

// Sketch button → open sketch canvas (scitex-ui SketchCanvas)
window.addEventListener("stx-shell:sketch", () => {
  if (sketchCanvas) {
    sketchCanvas.open();
  } else if (chatFileInput) {
    chatFileInput.click();
  }
});

// Mic button → toggle voice recording (scitex-ui VoiceRecorder)
window.addEventListener("stx-shell:mic-toggle", () => {
  if (!voiceRecorder) return;
  if (voiceRecorder.isRecording) {
    voiceRecorder.stop();
  } else {
    // STT adapter — uses browser SpeechRecognition as fallback
    // (full STT backend would come from scitex-app)
    voiceRecorder.start(
      {
        async transcribe(blob: Blob): Promise<string> {
          // Browser SpeechRecognition fallback (no server needed)
          console.log("[figrecipe] Voice recorded, size:", blob.size);
          // TODO: wire to scitex-app STT endpoint when available
          return "";
        },
      },
      (text: string) => {
        // Insert transcribed text into chat input
        const input = document.getElementById(
          "stx-shell-ai-input",
        ) as HTMLTextAreaElement | null;
        if (input && text) {
          input.value += text;
          input.focus();
        }
      },
    );
  }
});

// Settings — popover is in the template (standalone_shell.html).
// On first open, populate the App Skills section with figrecipe info.
let agentSourcesPopulated = false;
window.addEventListener("stx-shell:settings", () => {
  if (agentSourcesPopulated) return;
  agentSourcesPopulated = true;

  const container = document.getElementById("ai-agent-sources-content");
  if (!container) return;

  // Render figrecipe as the standalone app skill (matching scitex-cloud's format)
  container.innerHTML = `
    <div class="ai-config-category expanded" data-cat="App Skills">
      <div class="ai-config-category-header">
        <i class="fas fa-chevron-right ai-config-category-chevron"></i>
        <span class="ai-config-category-name">App Skills</span>
        <span class="ai-config-category-count">1/1</span>
      </div>
      <div class="ai-config-grid">
        <div class="ai-config-skill" data-skill="figrecipe">
          <div class="ai-config-card enabled">
            <i class="fas fa-chart-line ai-config-card-icon"></i>
            <div class="ai-config-card-info">
              <div class="ai-config-card-name">
                FigRecipe <span class="ai-config-active-tag">active</span>
              </div>
              <div class="ai-config-card-desc">Interactive figure editor — plt_*</div>
            </div>
            <label class="ai-config-toggle" onclick="event.stopPropagation()">
              <input type="checkbox" checked />
              <span class="ai-config-slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>`;

  // Bind category expand/collapse
  container
    .querySelectorAll<HTMLElement>(".ai-config-category-header")
    .forEach((header) => {
      header.addEventListener("click", () => {
        header.closest(".ai-config-category")?.classList.toggle("expanded");
      });
    });
});

// Wire file tree refresh when AI modifies files
document.addEventListener("stx-shell:files-changed", () => {
  shellFileTree.refresh();
});

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

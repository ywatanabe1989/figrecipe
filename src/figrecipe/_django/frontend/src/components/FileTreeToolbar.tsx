/** File tree toolbar — CRUD actions for recipe files.
 * Extracted from FileBrowser.tsx for use above scitex-ui FileBrowser. */

import { useCallback, useState } from "react";
import { api } from "../api/client";
import { useEditorStore } from "../store/useEditorStore";

export function FileTreeToolbar() {
  const { currentFile, loadFiles, switchFile, showToast } = useEditorStore();
  const [renaming, setRenaming] = useState<string | null>(null);
  const [newName, setNewName] = useState("");

  const handleNew = useCallback(async () => {
    try {
      const data = await api.post<{ path: string }>("api/new");
      showToast("Created new figure", "success");
      loadFiles();
      if (data.path) switchFile(data.path);
    } catch (e) {
      showToast(`Create failed: ${e}`, "error");
    }
  }, [loadFiles, switchFile, showToast]);

  const handleDelete = useCallback(async () => {
    if (!currentFile) return;
    const confirmed = window.confirm(
      `Delete "${currentFile}" and its associated files?`,
    );
    if (!confirmed) return;
    try {
      await api.post("api/delete", { path: currentFile });
      showToast("Deleted", "success");
      loadFiles();
    } catch (e) {
      showToast(`Delete failed: ${e}`, "error");
    }
  }, [currentFile, loadFiles, showToast]);

  const handleDuplicate = useCallback(async () => {
    if (!currentFile) return;
    try {
      const data = await api.post<{ path: string }>("api/duplicate", {
        path: currentFile,
      });
      showToast("Duplicated", "success");
      loadFiles();
      if (data.path) switchFile(data.path);
    } catch (e) {
      showToast(`Duplicate failed: ${e}`, "error");
    }
  }, [currentFile, loadFiles, switchFile, showToast]);

  const startRename = useCallback(() => {
    if (!currentFile) return;
    const baseName = currentFile.replace(/\.(yaml|yml)$/, "");
    setRenaming(currentFile);
    setNewName(baseName);
  }, [currentFile]);

  const commitRename = useCallback(async () => {
    if (!renaming || !newName.trim()) {
      setRenaming(null);
      return;
    }
    try {
      await api.post("api/rename", { path: renaming, new_name: newName });
      showToast("Renamed", "success");
      setRenaming(null);
      loadFiles();
    } catch (e) {
      showToast(`Rename failed: ${e}`, "error");
    }
  }, [renaming, newName, loadFiles, showToast]);

  const handleRefresh = useCallback(() => {
    loadFiles();
  }, [loadFiles]);

  return (
    <div className="file-browser__toolbar">
      <button
        className="pane-header-btn"
        onClick={handleNew}
        title="New figure"
        type="button"
      >
        <i className="fas fa-plus" />
      </button>
      <button
        className="pane-header-btn"
        onClick={handleDuplicate}
        title="Duplicate"
        type="button"
        disabled={!currentFile}
      >
        <i className="fas fa-copy" />
      </button>
      <button
        className="pane-header-btn"
        onClick={startRename}
        title="Rename"
        type="button"
        disabled={!currentFile}
      >
        <i className="fas fa-pen" />
      </button>
      <button
        className="pane-header-btn"
        onClick={handleDelete}
        title="Delete"
        type="button"
        disabled={!currentFile}
      >
        <i className="fas fa-trash" />
      </button>
      <div style={{ flex: 1 }} />
      <button
        className="pane-header-btn"
        onClick={handleRefresh}
        title="Refresh"
        type="button"
      >
        <i className="fas fa-sync" />
      </button>

      {renaming && (
        <div className="file-browser__rename" style={{ padding: "4px 8px" }}>
          <input
            className="property-input"
            style={{ width: "100%" }}
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onBlur={commitRename}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitRename();
              if (e.key === "Escape") setRenaming(null);
            }}
            autoFocus
          />
        </div>
      )}
    </div>
  );
}

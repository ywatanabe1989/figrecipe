/** File tree panel — browse, switch, and manage recipe files. */

import { useCallback, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";
import type { FileTreeItem } from "../../types/editor";

function TreeItem({ item, depth }: { item: FileTreeItem; depth: number }) {
  const { currentFile, switchFile } = useEditorStore();
  const [expanded, setExpanded] = useState(true);

  if (item.type === "directory") {
    return (
      <li>
        <div
          className={`file-tree__entry file-tree__entry--folder${expanded ? " expanded" : ""}`}
          style={{ paddingLeft: 8 + depth * 16 }}
          onClick={() => setExpanded(!expanded)}
        >
          <span className="file-tree__toggle">
            {expanded ? "\u25BC" : "\u25B6"}
          </span>
          <span className="file-tree__icon">
            {expanded ? "\u{1F4C2}" : "\u{1F4C1}"}
          </span>
          <span className="file-tree__name">{item.name}</span>
          <span className="file-tree__badge">{item.children?.length ?? 0}</span>
        </div>
        {expanded && item.children && (
          <ul className="file-tree__children">
            {item.children.map((child) => (
              <TreeItem key={child.path} item={child} depth={depth + 1} />
            ))}
          </ul>
        )}
      </li>
    );
  }

  const isCurrent = item.path === currentFile;
  return (
    <li>
      <div
        className={`file-tree__entry${isCurrent ? " current" : ""}${item.has_image ? " has-image" : ""}`}
        style={{ paddingLeft: 8 + depth * 16 }}
        onClick={() => !isCurrent && switchFile(item.path)}
      >
        <span className="file-tree__icon">
          {item.has_image ? "\u{1F4CA}" : "\u{1F4C4}"}
        </span>
        <span className="file-tree__name">{item.name}</span>
        {item.has_image && <span className="file-tree__badge">PNG</span>}
      </div>
    </li>
  );
}

interface FileBrowserProps {
  headerProps?: Record<string, unknown>;
}

export function FileBrowser({ headerProps }: FileBrowserProps) {
  const { files, currentFile, loadFiles, switchFile, showToast } =
    useEditorStore();
  const [renaming, setRenaming] = useState<string | null>(null);
  const [newName, setNewName] = useState("");

  const handleRefresh = useCallback(() => {
    loadFiles();
  }, [loadFiles]);

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

  return (
    <div className="file-browser">
      <div className="file-browser__header" {...headerProps}>
        <span className="sidebar-title">FILES</span>
        <h3>Files</h3>
        <div className="file-browser__actions">
          <button
            className="file-browser__btn"
            onClick={handleNew}
            title="New figure"
          >
            +
          </button>
          <button
            className="file-browser__btn"
            onClick={handleDuplicate}
            title="Duplicate"
            disabled={!currentFile}
          >
            &#x29C9;
          </button>
          <button
            className="file-browser__btn"
            onClick={startRename}
            title="Rename"
            disabled={!currentFile}
          >
            &#x270E;
          </button>
          <button
            className="file-browser__btn"
            onClick={handleDelete}
            title="Delete"
            disabled={!currentFile}
          >
            &#x2715;
          </button>
          <button
            className="file-browser__btn"
            onClick={handleRefresh}
            title="Refresh"
          >
            &#x21BB;
          </button>
        </div>
      </div>

      {renaming && (
        <div className="file-browser__rename">
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

      <ul className="file-tree">
        {files.length === 0 ? (
          <li className="file-tree__empty">
            <p>No recipe files</p>
          </li>
        ) : (
          files.map((item) => (
            <TreeItem key={item.path} item={item} depth={0} />
          ))
        )}
      </ul>
    </div>
  );
}

/** Left-most pane — File tree with vis_app pane-header. */

import { useEditorStore } from "../../store/useEditorStore";
import { FileBrowser } from "../FileBrowser/FileBrowser";

interface Props {
  collapsed: boolean;
  toggleCollapse: () => void;
}

export function FileTreePane({ collapsed, toggleCollapse }: Props) {
  const { files } = useEditorStore();

  const fileCount = files.reduce((n, item) => {
    if (item.type === "directory") return n + (item.children?.length ?? 0);
    return n + 1;
  }, 0);

  return (
    <>
      {/* vis_app .pane-header */}
      <div className="pane-header">
        <span className="pane-header-title">
          <i className="fas fa-folder-open" />
          Files
        </span>

        {fileCount > 0 && <span className="badge badge-type">{fileCount}</span>}

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Collapse toggle */}
        <button
          className="pane-header-btn panel-toggle-btn"
          onClick={toggleCollapse}
          title={collapsed ? "Expand" : "Collapse"}
          type="button"
        >
          <i className={`fas fa-chevron-${collapsed ? "right" : "left"}`} />
        </button>

        {/* Vertical title (visible only when collapsed via CSS) */}
        <span className="panel-title">Files</span>
      </div>

      {/* Pane content */}
      <div className="pane-content">
        <FileBrowser />
      </div>
    </>
  );
}

/** Right pane — Properties/Details with vis_app pane-header. */

import { useEditorStore } from "../../store/useEditorStore";
import { Properties } from "../Properties/Properties";

interface PropertiesPaneProps {
  onHeaderDoubleClick?: () => void;
}

export function PropertiesPane({ onHeaderDoubleClick }: PropertiesPaneProps) {
  const { selectedElement, selectedBbox } = useEditorStore();

  return (
    <>
      {/* vis_app .pane-header */}
      <div className="pane-header" onDoubleClick={onHeaderDoubleClick}>
        {/* Details title */}
        <span className="pane-header-title">
          <i className="fas fa-sliders-h" />
          Details
        </span>

        {/* Selected type badge */}
        {selectedElement && selectedBbox?.type && (
          <span className="badge badge-type">{selectedBbox.type}</span>
        )}

        {/* Vertical title (visible only when collapsed via CSS) */}
        <span className="panel-title">
          <i className="fas fa-sliders-h" />
          Details
        </span>
      </div>

      {/* Pane content */}
      <div className="pane-content">
        <Properties />
      </div>
    </>
  );
}

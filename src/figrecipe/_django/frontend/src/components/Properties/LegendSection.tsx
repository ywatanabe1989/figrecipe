/** Legend sub-panel — visibility toggle and location dropdown. */

import { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";
import { PropRow } from "./PropRow";
import { PropSection } from "./PropSection";

interface LegendInfo {
  has_legend: boolean;
  visible: boolean;
  loc: string;
}

const LEGEND_LOCATIONS = [
  { label: "Best", value: "best" },
  { label: "Upper Right", value: "upper right" },
  { label: "Upper Left", value: "upper left" },
  { label: "Lower Left", value: "lower left" },
  { label: "Lower Right", value: "lower right" },
  { label: "Right", value: "right" },
  { label: "Center Left", value: "center left" },
  { label: "Center Right", value: "center right" },
  { label: "Lower Center", value: "lower center" },
  { label: "Upper Center", value: "upper center" },
  { label: "Center", value: "center" },
];

export function LegendSection({ axIndex }: { axIndex: number }) {
  const [info, setInfo] = useState<LegendInfo | null>(null);
  const { showToast, loadPreview } = useEditorStore();

  useEffect(() => {
    api
      .get<LegendInfo>(`get_legend_info?ax_index=${axIndex}`)
      .then(setInfo)
      .catch(() => setInfo(null));
  }, [axIndex]);

  const updateLegend = useCallback(
    async (updates: Record<string, unknown>) => {
      try {
        await api.post("update_legend_position", {
          ax_index: axIndex,
          ...updates,
        });
        loadPreview();
      } catch (e) {
        showToast(`Legend update failed: ${e}`, "error");
      }
    },
    [axIndex, loadPreview, showToast],
  );

  if (!info?.has_legend) return null;

  return (
    <PropSection title="Legend" defaultOpen={false}>
      <PropRow
        label="Visible"
        value={info.visible}
        editable
        type="checkbox"
        onChange={(v) => updateLegend({ visible: v })}
      />
      <PropRow
        label="Location"
        value={info.loc}
        editable
        type="select"
        options={LEGEND_LOCATIONS}
        onChange={(v) => updateLegend({ loc: v })}
      />
    </PropSection>
  );
}

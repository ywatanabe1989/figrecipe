/** Labels sub-panel — editable title, xlabel, ylabel for an axes. */

import { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";
import { DebouncedInput } from "./DebouncedInput";
import { PropSection } from "./PropSection";

interface Labels {
  title: string;
  xlabel: string;
  ylabel: string;
  suptitle: string;
}

export function LabelsSection({ axIndex }: { axIndex: number }) {
  const [labels, setLabels] = useState<Labels | null>(null);
  const { showToast, loadPreview } = useEditorStore();

  useEffect(() => {
    api
      .get<Labels>(`get_labels?ax_index=${axIndex}`)
      .then(setLabels)
      .catch(() => setLabels(null));
  }, [axIndex]);

  const updateLabel = useCallback(
    async (labelType: string, text: string) => {
      try {
        await api.post("update_label", {
          label_type: labelType,
          text,
          ax_index: axIndex,
        });
        loadPreview();
      } catch (e) {
        showToast(`Label update failed: ${e}`, "error");
      }
    },
    [axIndex, loadPreview, showToast],
  );

  if (!labels) return null;

  return (
    <PropSection title="Labels">
      <DebouncedInput
        label="Title"
        value={labels.title}
        onCommit={(v) => updateLabel("title", v)}
      />
      <DebouncedInput
        label="X Label"
        value={labels.xlabel}
        onCommit={(v) => updateLabel("xlabel", v)}
      />
      <DebouncedInput
        label="Y Label"
        value={labels.ylabel}
        onCommit={(v) => updateLabel("ylabel", v)}
      />
    </PropSection>
  );
}

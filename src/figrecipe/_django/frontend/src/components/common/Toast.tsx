/** Toast notification component. */

import { useEditorStore } from "../../store/useEditorStore";

export function Toast() {
  const { toast, clearToast } = useEditorStore();

  if (!toast) return null;

  return (
    <div className={`toast toast--${toast.type}`} onClick={clearToast}>
      {toast.message}
    </div>
  );
}

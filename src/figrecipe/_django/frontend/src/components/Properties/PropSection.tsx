/** Collapsible section matching vis_app properties panel style. */

import { useState } from "react";

export function PropSection({
  title,
  defaultOpen = true,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`prop-section${open ? "" : " collapsed"}`}>
      <button
        className="prop-section__header"
        onClick={() => setOpen(!open)}
        type="button"
      >
        <span className="prop-section__chevron">
          {open ? "\u25BE" : "\u25B8"}
        </span>
        <span>{title}</span>
      </button>
      {open && <div className="prop-section__body">{children}</div>}
    </div>
  );
}

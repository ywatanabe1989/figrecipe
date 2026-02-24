/** Ribbon group — labeled cluster of buttons with optional separator. */

import type { ReactNode } from "react";

interface Props {
  label: string;
  children: ReactNode;
  separator?: boolean;
}

export function RibbonGroup({ label, children, separator = true }: Props) {
  return (
    <>
      <div className="ribbon-group">
        <span className="ribbon-group-label">{label}</span>
        <div className="ribbon-group-buttons">{children}</div>
      </div>
      {separator && <div className="ribbon-separator" />}
    </>
  );
}

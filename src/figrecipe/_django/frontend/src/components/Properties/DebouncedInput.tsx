/** Text input that only fires onChange on blur or Enter — avoids per-keystroke API calls. */

import { useCallback, useEffect, useRef, useState } from "react";

export function DebouncedInput({
  label,
  value: initialValue,
  onCommit,
}: {
  label: string;
  value: string;
  onCommit: (val: string) => void;
}) {
  const [val, setVal] = useState(initialValue);
  const committed = useRef(false);

  useEffect(() => {
    setVal(initialValue);
    committed.current = false;
  }, [initialValue]);

  const commit = useCallback(() => {
    if (!committed.current && val !== initialValue) {
      committed.current = true;
      onCommit(val);
    }
  }, [val, initialValue, onCommit]);

  return (
    <div className="property-row">
      <div className="property-group">
        <span className="property-label">{label}</span>
        <input
          className="property-input"
          type="text"
          value={val}
          onChange={(e) => {
            setVal(e.target.value);
            committed.current = false;
          }}
          onBlur={commit}
          onKeyDown={(e) => {
            if (e.key === "Enter") commit();
          }}
        />
      </div>
    </div>
  );
}

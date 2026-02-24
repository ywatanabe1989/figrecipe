/** Panel letter badge (A, B, C...) at top-left of each figure. */

import { useCallback, useEffect, useRef, useState } from "react";

interface Props {
  letter?: string;
  onChange: (letter: string) => void;
}

export function PanelLetterOverlay({ letter, onChange }: Props) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(letter ?? "");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => setText(letter ?? ""), [letter]);
  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  const save = useCallback(() => {
    setEditing(false);
    if (text.trim()) onChange(text.trim());
  }, [text, onChange]);

  if (!letter) return null;

  if (editing) {
    return (
      <input
        ref={inputRef}
        className="panel-letter-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onBlur={save}
        onKeyDown={(e) => {
          if (e.key === "Enter") save();
          if (e.key === "Escape") {
            setText(letter);
            setEditing(false);
          }
          e.stopPropagation();
        }}
        onClick={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
      />
    );
  }

  return (
    <span
      className="panel-letter"
      onDoubleClick={(e) => {
        e.stopPropagation();
        setEditing(true);
      }}
      title="Double-click to edit"
    >
      {letter}
    </span>
  );
}

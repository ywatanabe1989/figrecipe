/** Undo/Redo state history for canvas operations.
 *
 * Tracks snapshots of figure positions, placements, and overrides.
 * Max 50 history states. Push on every user action that modifies canvas.
 */

import { useEditorStore } from "../store/useEditorStore";
import type { PlacedFigure, StyleOverrides } from "../types/editor";

interface Snapshot {
  placedFigures: PlacedFigure[];
  overrides: StyleOverrides;
}

const MAX_HISTORY = 50;

let history: Snapshot[] = [];
let pointer = -1;

function takeSnapshot(): Snapshot {
  const { placedFigures, overrides } = useEditorStore.getState();
  return {
    placedFigures: placedFigures.map((f) => ({ ...f })),
    overrides: { ...overrides },
  };
}

/** Push current state onto history stack. Call after every user action. */
export function pushUndoState(): void {
  const snap = takeSnapshot();

  // Discard any redo states ahead of pointer
  history = history.slice(0, pointer + 1);
  history.push(snap);

  // Cap at max
  if (history.length > MAX_HISTORY) {
    history = history.slice(history.length - MAX_HISTORY);
  }
  pointer = history.length - 1;
}

/** Undo — restore previous state. */
export function undo(): boolean {
  if (pointer <= 0) return false;
  pointer--;
  applySnapshot(history[pointer]);
  return true;
}

/** Redo — restore next state. */
export function redo(): boolean {
  if (pointer >= history.length - 1) return false;
  pointer++;
  applySnapshot(history[pointer]);
  return true;
}

/** Check if undo/redo is available. */
export function canUndo(): boolean {
  return pointer > 0;
}

export function canRedo(): boolean {
  return pointer < history.length - 1;
}

/** Initialize history with current state. Call once on app load. */
export function initUndoHistory(): void {
  history = [takeSnapshot()];
  pointer = 0;
}

function applySnapshot(snap: Snapshot): void {
  useEditorStore.setState({
    placedFigures: snap.placedFigures.map((f) => ({ ...f })),
    overrides: { ...snap.overrides },
  });
}

/** figrecipe-editor — public API barrel export. */

export { FigrecipeEditor } from "./FigrecipeEditor";
export type { FigrecipeEditorProps } from "./FigrecipeEditor";
export type { BBox, StatBracket, CallRecord } from "./types/editor";
export { useEditorStore } from "./store/useEditorStore";
export { setApiBase, setWorkingDir, setRecipe } from "./api/client";

/** figrecipe bridge — barrel export. */

export {
  mountFigrecipeEditor,
  unmountFigrecipeEditor,
  switchRecipeFile,
} from "./MountPoint";

export { emitEvent, onEvent } from "./EventBus";
export type { FigrecipeEventMap, FigrecipeEventName } from "./EventBus";

export {
  wireWorkspaceBridge,
  unwireWorkspaceBridge,
  runStatAndRenderBracket,
} from "./WorkspaceIntegration";

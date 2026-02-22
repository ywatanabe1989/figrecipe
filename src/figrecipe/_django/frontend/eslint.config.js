// ESLint v9 config for figrecipe frontend
// TypeScript linting is handled by tsc (via `npm run build`).
// ESLint here only catches JS-level issues; TS files use tsc for type checking.
export default [
  {
    ignores: ["**/*.ts", "**/*.tsx", "dist/**", "node_modules/**"],
  },
];

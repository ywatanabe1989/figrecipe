// ESLint v9 config for figrecipe project root.
// TypeScript checking is handled by tsc (via `npm run build` in frontend/).
// ESLint here only catches JS-level issues in non-TS files.
export default [
  {
    ignores: [
      "**/*.ts",
      "**/*.tsx",
      "**/node_modules/**",
      "**/dist/**",
      "**/*.min.js",
    ],
  },
];

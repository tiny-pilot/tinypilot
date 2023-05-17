module.exports = {
  env: {
    node: true,
    browser: true,
    es2022: true,
  },
  parserOptions: {
    sourceType: "module",
  },
  plugins: ["html"],
  extends: ["eslint:recommended"],
  rules: {
    "block-scoped-var": "error",
    "capitalized-comments": [
      "error",
      "always",
      {
        ignoreConsecutiveComments: true,
        // We want to allow inline comments to document a parameter like
        // foo(/*force=*/ true). We're not married to this particular pattern
        // for variable names, and we can update it if we have variable names
        // that fall outside the pattern.
        ignorePattern: `[a-zA-Z]+=`,
      },
    ],
    eqeqeq: "error",
    // This will produce an error for console.log or console.warn in production
    // and a warning in development.
    "no-console": [
      process.env.NODE_ENV === "production" ? "error" : "warn",
      { allow: ["error", "debug"] },
    ],
    "no-constant-binary-expression": "error",
    "no-duplicate-imports": "error",
    "no-lonely-if": "error",
    "no-unused-private-class-members": "error",
    "no-useless-return": "error",
    "no-var": "error",
    "one-var-declaration-per-line": "error",
    "prefer-const": "error",
  },
  ignorePatterns: ["app/static/third-party", "playwright-report", "venv"],
};

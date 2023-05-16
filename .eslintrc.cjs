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
    // This will produce an error for console.log or console.warn in production
    // and a warning in development.
    "no-console": [
      process.env.NODE_ENV === "production" ? "error" : "warn",
      { allow: ["error", "debug"] },
    ],
  },
  ignorePatterns: ["app/static/third-party", "playwright-report", "venv"],
};

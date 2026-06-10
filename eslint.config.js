import js from "@eslint/js";
import html from "eslint-plugin-html";
import globals from "globals";

export default [
  {
    ignores: [
      "app/static/third-party/**",
      "app/templates/components/debug-mode.html",
      "playwright-report/**",
      "**/venv/**",
      "e2e-results/**",
    ],
  },
  js.configs.recommended,
  {
    files: ["**/*.js", "**/*.html"],
    plugins: { html },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        ...globals.node,
        ...globals.browser,
      },
    },
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
      "no-duplicate-imports": "error",
      "no-lonely-if": "error",
      "no-param-reassign": "error",
      "no-useless-return": "error",
      "no-var": "error",
      "prefer-const": "error",
    },
  },
];

import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";
import globals from "globals";

export default [
    {
        ignores: [
            "node_modules",
            "dist",
            ".nyc_output",
            "coverage-js",
            "session_security/static/session_security/coverage/**",
            ".venv/**",
        ],
    },
    {
        files: ["session_security/static/session_security/**/*.js"],
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
            },
        },
        rules: {
            ...js.configs.recommended.rules,
            curly: "error",
        },
    },
    eslintConfigPrettier,
];

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
            "django_session_security_continued/static/session_security/coverage/**",
            ".venv/**",
        ],
    },
    {
        files: ["django_session_security_continued/static/session_security/**/*.js"],
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

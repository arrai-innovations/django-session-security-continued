import { defineConfig } from "vite";
import istanbul from "vite-plugin-istanbul";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = fileURLToPath(new URL(".", import.meta.url));
const entryFile = path.resolve(rootDir, "session_security/static/session_security/script.js");
const outDir = path.resolve(rootDir, "session_security/static/session_security/coverage");

export default defineConfig(() => {
  const coverageEnabled = process.env.COVERAGE === "true";
  return {
    build: {
      lib: {
        entry: entryFile,
        name: "SessionSecurityBundle",
        fileName: () => "script.js",
        formats: ["iife"],
      },
      outDir,
      emptyOutDir: true,
      minify: false,
      sourcemap: true,
    },
    plugins: coverageEnabled
      ? [
          istanbul({
            include: ["**/session_security/static/session_security/**/*.js"],
            extension: [".js"],
            requireEnv: false,
            cypress: false,
            vitest: false,
            forceBuildInstrument: true,
          }),
        ]
      : [],
  };
});

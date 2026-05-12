import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import tseslint from "typescript-eslint";

const compat = new FlatCompat({
  baseDirectory: dirname(fileURLToPath(import.meta.url)),
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

const eslintConfig = [
  {
    ignores: [".next/**", "node_modules/**", "coverage/**", "out/**", "next-env.d.ts"],
  },
  ...compat.extends("next/core-web-vitals"),
  ...tseslint.configs.recommended,
];

export default eslintConfig;

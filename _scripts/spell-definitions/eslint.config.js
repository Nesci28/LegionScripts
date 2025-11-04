/** @type {import("eslint").Linter.Config[]} */

module.exports = [
  ...require("@okidoo/eslint-config/node-biome-2.2.4-eslint"),
  {
    ignores: [
      "generated",
    ],
  }
];
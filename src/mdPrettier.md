---
author: malys
description: Beautify md file.
pageDecoration.prefix: "🛎️ "
name: "Library/Malys/mdPrettier"
tags: meta/library
---
# Md Prettier

Beautify markdown.

## Code

```space-lua
local prettier = js.import("https://cdn.jsdelivr.net/npm/prettier/standalone/+esm")
local prettierMarkdown = js.import("https://cdn.jsdelivr.net/npm/prettier/plugins/markdown/+esm")

local function formatText(text)
  return prettier.format(text, {
    parser = "markdown",
    plugins = { prettierMarkdown },

    printWidth = 160,
    proseWrap = "preserve",

    -- These DO NOT affect markdown tables
    useTabs = true,
    tabWidth = 4,
  })
end

local function formatDocument()
  local text = editor.getText()
  local formattedText = formatText(text)
  editor.setText(formattedText)
end

command.define {
  name = "Beautify: markdown",
  run = formatDocument,
}
```

**Important Notes:**

- **Placement:** `prettier-ignore` _must_ be the very first line within the code
  fence. Any leading whitespace will cause it to be ignored.
- **Scope:** `prettier-ignore` applies to the entire code fence it's placed in.
- **Alternative:** If you want to disable formatting for a specific section of
  code _within_ a code fence, you can use `prettier-ignore` on a single line:

## Changelog

- 2026-05-29:
    - cleanup: declared `formatText`/`formatDocument` as `local function` instead of leaking them as globals
- 2026-01-25:
    - feat: add option and ignore code

## Community

[Silverbullet forum](https://community.silverbullet.md/t/markdown-formatter-for-silverbullet/3071)

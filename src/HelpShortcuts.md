---
author: malys
description: Display most commun shortcuts.
pageDecoration.prefix: "🆘 "
name: "Library/Malys/HelpShortcuts"
tags: meta/library
---
# Help: Shortcuts
Display helper on demand.

```space-lua
command.define {
  name = "Help: shortcuts",
  key = "Ctrl-h",
  run = function()
    local messages={ "shift-alt-e header picker",  "ctrl-alt-t tag picker","alt-c: copy nearest","shift-ctrl-c:  cursor position","alt-ctrl-n: new child","alt-ctrl-s: new sibling","ctrl-Alt-1: code block","!!last monday: chronos"}
    for _, message in ipairs(messages) do
      editor.flashNotification(message, "info")
    end
  end
}
```

## Changelog

* 2026-05-29:
  * cleanup: iterate the messages list with `ipairs` (guaranteed order) instead of `pairs`
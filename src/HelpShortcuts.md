---
author: malys
description: Display most commun shortcuts.
---
# Help: Shortcuts
Display helper on demand.

```space-lua
command.define {
  name = "Help: shortcuts",
  key = "Ctrl-h",
  run = function()
    local messages={ "ctrl-shift-h header picker",  "ctrl-shift-t tag picker","alt-c: copy nearest","shift-ctrl-c:  cursor position","alt-ctrl-n: new child","alt-ctrl-s: new sibling","ctrl-Alt-1: code block","!!last monday: chronos"}
    for i in pairs(messages) do
      editor.flashNotification(messages[i], "info")
    end
  end
}
```
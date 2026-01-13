---
author: malys
description: Quickly insert bash code.
name: "Library/Malys/BashCode"
tags: meta/library
---
# Bash code
Quickly insert bash code.

```space-lua
slashcommand.define {
  name = "bash",
  description="bash code",
  run = function()
tpl=[[```bash
#|^|
```]]
  editor.insertAtCursor(tpl, false, true)
  end
}

```


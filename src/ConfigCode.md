---
author: malys
description: Quickly insert config code.
name: "Library/Malys/ConfigCode"
tags: meta/library
---
# Config code
Template for Utility library with right priority.

```space-lua
slashcommand.define {
  name = "config",
  description="config code",
  run = function()
tpl=[[```space-lua
--priority: 19        
#|^|
```]]
  editor.insertAtCursor(tpl, false, true)
  end
}

```


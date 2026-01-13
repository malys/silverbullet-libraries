---
author: malys
description: Quickly insert utility code.
name: "Library/Malys/UtilityCode"
tags: meta/library
---
# Utility code
Template for Utility library with right priority.

```space-lua
slashcommand.define {
  name = "utility",
  description="utility code",
  run = function()
tpl=[[```space-lua
--priority: 15     
--|^|
```]]
  editor.insertAtCursor(tpl, false, true)
  end
}

```


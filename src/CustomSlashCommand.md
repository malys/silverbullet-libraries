---
author: malys
description: custom slash commands.
pageDecoration.prefix: "🆘 "
name: "Library/Malys/CustomSlashCommand"
tags: meta/library
---
# Custom slashcommand editor

## Lua
```space-lua
slashcommand.define {
  name = "luaeditor",
  description= "insert lua editor",
  run = function()
  local tpl=[[${mls.embedUrl("https://glot.io/new/lua","100%","1000px")}]]
  editor.insertAtCursor(tpl, false, true)
  end
}
slashcommand.define {
  name = "luacheck: globals",
  description= "insert lua editor",
  run = function()
  local tpl=[[-- luacheck: globals |^|]]
  editor.insertAtCursor(tpl, false, true)
  end
}
```
## Plantuml
```space-lua
slashcommand.define {
  name = "plantumleditor",
  description= "insert plantuml editor",
  run = function()
  local tpl=[[${mls.embedUrl("https://plantuml.online/uml/","100%","1000px")}]]
  editor.insertAtCursor(tpl, false, true)
  end
}
```

## Json & Lua md table convertor
```space-lua
slashcommand.define {
  name = "toMdTable",
  description= "convert Json or Lua table to md table",
  run = function()
    local data = editor.prompt("Lua or Json array")
    editor.insertAtCursor(table.toMd(data), false, true)
  end
}
```

## Bash code

```space-lua
slashcommand.define {
  name = "bash",
  description="bash code",
  run = function()
local tpl=[[```bash
#|^|
```]]
  editor.insertAtCursor(tpl, false, true)
  end
}
```

## Utility code template

```space-lua
slashcommand.define {
  name = "utility",
  description="utility code",
  run = function()
local tpl=[[```space-lua
--priority: 15     
--|^|
```]]
  editor.insertAtCursor(tpl, false, true)
  end
}
```

## Config code template

```space-lua
slashcommand.define {
  name = "config",
  description="config code",
  run = function()
local tpl=[[```space-lua
--priority: 19        
#|^|
```]]
  editor.insertAtCursor(tpl, false, true)
  end
}
```

## Changelog

* 2026-05-29:
  * fix: `toMdTable` referenced an undefined `pageName` and called `editor.navigate` for no reason; removed the stray line
  * fix: the `mood` command used `slashCommand.define` (wrong casing); now `slashcommand.define`
  * cleanup: declared the `tpl` template variables `local` instead of leaking them as globals
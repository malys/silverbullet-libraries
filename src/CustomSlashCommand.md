---
author: malys
description: custom slash commands.
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
  tpl=[[${mls.embedUrl("https://glot.io/new/lua","100%","1000px")}]]
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
  tpl=[[${mls.embedUrl("https://plantuml.online/uml/","100%","1000px")}]]
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
    if pageName then editor.navigate(pageName) end
    editor.insertAtCursor(table.toMd(data), false, true)
  end
}
```

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
  tpl=[[${mls.embedUrl("https://glot.io/new/lua","100%","1000px")}]]
  editor.insertAtCursor(tpl, false, true)
  end
}
slashcommand.define {
  name = "luacheck: globals",
  description= "insert lua editor",
  run = function()
  tpl=[[-- luacheck: globals |^|]]
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

# Mood

```space-lua
slashCommand.define {  
  name = "mood",  
  description = "Insert daily health tracking",  
  run = function()  
    -- Collect inputs using dropdown dialogs  
    local night =mls.table.render("Night","evaluation")  
    local mMood = mls.table.render("Morning mood", "mood")  
    local eMood = mls.table.render("Night mood","mood")  
    local recover = mls.table.render("Recover","posneg")
    local pacing =  mls.table.render("Pacing","logical")  
    local crash =  mls.table.render("Crash","logical")  
    local comments =mls.table.render("Comment")  
      
    -- Build template with collected values  
    local template = string.format("| %s | %s    | %s           | %s                | %s                 | %s                   | %s             | %s              | %s                          |\n",  
      os.date("%Y-%m-%d"),  
      os.date("%a", os.time()):sub(1,2):upper(),  
      night or "3",  
      mMood or "3",  
      eMood  or "3",   
      recover or "0",  
      pacing or "1",  
      crash or "1",  
      comments or ""  
    )  
    editor.insertAtCursor(template)  
  end  
}
```

## Bash code

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

## Utility code template

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

## Config code template

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
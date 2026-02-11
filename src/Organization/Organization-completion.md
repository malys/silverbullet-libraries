---
author: malys
description: Organization autocompletion on person @ and company #.
name: "Library/Malys/Organization-completion"
tags: meta/library
---
# Autocompletion

## Person
```space-lua
event.listen {  
  name = "editor:complete",  
  run = function(e)  
    local linePrefix = e.data.linePrefix or ""  
    local pos = e.data.pos or 0  
  
    local match = string.match(linePrefix, "@([a-zA-Z0-9_]*)$")  
    if not match then  
      return  
    end  
  
    local people = query[[ from p = index.tag("person")]]  
    local opts = {}  
  
    for _, p in ipairs(people) do  
      local label = (p.person.first_name or "") .. " " .. (p.person.last_name or "")  
      local completionText = "[[" .. p.ref .. "|" .. label .. "]]"  
      if string.len(string.trim(label))>0 then  
        table.insert(opts, {  
          label = label,  
          detail = p.ref,
          apply = function()  
            editor.dispatch({  
              changes = {  
                from = pos - string.len(match) - 1,  
                to = pos,  
                insert = completionText  
              }  
            })  
          end
        }) 
      end  
    end  
  
    return {  
      from = pos - string.len(match),  
      options = opts  
    }  
  end  
}
```

## Company

```space-lua
event.listen {  
  name = "editor:complete",  
  run = function(e)  
    local linePrefix = e.data.linePrefix or ""  
    local pos = e.data.pos or 0  
  
    local match = string.match(linePrefix, "%$([a-zA-Z0-9_]*)$")  
    if not match then  
      return  
    end  
  
    local people = query[[ from p = index.tag("company")]]  
    local opts = {}  
  
    for _, p in ipairs(people) do  
      local label = (p.company.name or "")
      local completionText = "[[" .. p.ref .. "|" .. label .. "]]"  
        
      table.insert(opts, {  
        label = label,  
        detail = p.ref,
        apply = function()  
          editor.dispatch({  
            changes = {  
              from = pos - string.len(match) - 1,  
              to = pos,  
              insert = completionText  
            }  
          })  
        end
      })  
    end  
  
    return {  
      from = pos - string.len(match),  
      options = opts  
    }  
  end  
}
```


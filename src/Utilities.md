---
author: malys
description: List of reusable functions.
name: "Library/Malys/Utilities"
tags: meta/library
---
# Utilities

## Debug

### How to enable debug mode

* Create space-lua with:
```lua
LOG_ENABLE=true
```

* Reload system.
* Open Chrome Console
* Add filter “[Client] [DEBUG]“
## Code
```space-lua
-- priority: 11
mls=mls or {}

-- Convert meeting note title
function mls.getmeetingTitle()
  local t=string.split(string.split(editor.getCurrentPage(),"/")[#string.split(editor.getCurrentPage(),"/")],"_")
  table.remove(t,1)
  t=table.concat(t, " ")
  return t
end

-- Embed external resources
function mls.embedUrl(specOrUrl,w,h) 
  local width = w or "100%"
  local height = h or "400px"
  return widget.html(dom.iframe {
    src=specOrUrl,
    style="width: " .. width .. "; height: " .. height
  })
end

---------------------------------------------
---- Debug  ---
---------------------------------------------
-- Pretty-print any Lua value (tables included)
local function dump(value, depth)
  --print("[DEBUG][TYPE]"..type(value))
  depth = depth or 0
  if type(value) ~= "table" or (type(value) == "string" and value ~= "[object Object]") then
    return value
  end

  -- Prevent going too deep (avoid infinite recursion)
  if depth > 5 then
    return "{ ... }"
  end

  local indent = string.rep("  ", depth)
  local next_indent = string.rep("  ", depth + 1)

  local parts = {}
  table.insert(parts, "{")

  for k, v in pairs(value) do
    local key = tostring(k)
    local val
    if type(v) == "table" then
      val = dump(v, depth + 1)
    else
      val = v
    end

    table.insert(parts, next_indent .. tostring(key) .. " = " .. tostring(val) .. ",")
  end

  table.insert(parts, indent .. "}")

  return table.concat(parts, "\n")
end


function mls.debug(message, prefix)
  if not LOG_ENABLE then
    return message
  end
  local log_message = dump(message)

  local result = "[DEBUG]"
  if prefix then
    result = result .. "[" .. tostring(prefix) .. "]"
  end

  result = result .. " " .. tostring(log_message)
  print(result)
  return result
end


---------------------------------------------
---- Code Block code extraction ---
---------------------------------------------
-- Get child of node  
local getChild = function(node, type)
  for _, child in ipairs(node.children) do
    if child.type == type then
      return child
    end
  end
end

-- Get text of Node
local getText = function(node)
  if not node then
    return nil
  end
  if node.text then
    return node.text
  else
    for _, child in ipairs(node.children) do
      local text = getText(child)
      if text then
        return text
      end
    end
  end
end

-- Find codeblock
local findMyFence = function(node,blockId)
    if not node.children then
      return nil
    end
    for _, child in ipairs(node.children) do
        --debug_log(child)
        if child.type == "FencedCode" then
          local info = getText(getChild(child, "CodeInfo"))
          --debug_log(info)
          if info  and info:find(blockId) then
            return getChild(child, "CodeText")
          end
        end
        local result= findMyFence(child,blockId)
        if resul ~=nil then
          return result
        end
      --break --  for loop
    end --for
end

-- Get code source in md codeblock
function mls.getCodeBlock  (page,blockId,token,text)
  local tree = markdown.parseMarkdown(space.readPage(page))
  --debug_log(tree)
  if tree then
    local fence = findMyFence(tree,blockId)
    --debug_log(fence)
    if fence then
      local result=fence.children[1].text
      if token == nil or text==nill then
        return result
      else
        return string.gsub(result, token, text)
      end
    end
  end
  return "Error"
end

function mls.parseISODate(isoDate)
    local pattern = "(%d+)%-(%d+)%-(%d+)%a(%d+)%:(%d+)%:([%d%.]+)([Z%+%-])(%d?%d?)%:?(%d?%d?)"
    local year, month, day, hour, minute, 
        seconds, offsetsign, offsethour, offsetmin = json_date:match(pattern)
    local timestamp = os.time{year = year, month = month, 
        day = day, hour = hour, min = minute, sec = seconds}
    local offset = 0
    if offsetsign ~= 'Z' then
      offset = tonumber(offsethour) * 60 + tonumber(offsetmin)
      if xoffset == "-" then offset = offset * -1 end
    end
    
    return timestamp + offset
end
```



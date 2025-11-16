---
author: malys
description: List of reusable functions.
name: "Library/Malys/Utilities"
tags: meta/library
---
# Utilities
```space-lua
utilities=utilities or {}

-- Convert meeting note title
function utilities.getmeetingTitle()
  local t=string.split(string.split(editor.getCurrentPage(),"/")[#string.split(editor.getCurrentPage(),"/")],"_")
  table.remove(t,1)
  t=table.concat(t, " ")
  return t
end

-- Embed external resources
function utilities.embedUrl(specOrUrl,w,h) 
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
function utilities.debug(message, prefix)
  local result=message
  if LOG_ENABLE or true then
    local log_message = ""
    if type(message) == "table" then
      log_message = tostring(message)
    else
      -- Assume it's a string, number, boolean, or nil
      log_message = tostring(message)
    end
    result="[DEBUG] " .. log_message
    if prefix ~= nil then 
      result="[DEBUG]"..  "["..prefix.."] " .. log_message
    end
    js.log(result)  
  end
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
function utilities.getCodeBlock  (page,blockId,token,text)
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
```


${utilities.debug("test")}
${      utilities.debug("mode:"..true)}

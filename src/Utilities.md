---
author: malys
description: List of reusable functions.
name: "Library/Malys/Utilities"
tags: meta/library
---
# Utilities

*   `mls.getmeetingTitle()`: Extracts meeting title from page URL.
*   `mls.embedUrl(url, w, h)`: Embeds a URL using an iframe (width & height optional).
*   `mls.debug(message, prefix)`: Prints debug message (if `LOG_ENABLE` is true).
*   `mls.getCodeBlock(page, blockId, token, text)`: Retrieves code from a Markdown code block by ID, with optional token replacement.
*   `mls.parseISODate(isoDate)`: Parses an ISO date string to a timestamp (potential error with `xoffset`).
*   `mls.getStdlibInternal()`: Gets a list of internal API keys (cached).
*   `mls.positionToLineColumn(text, pos)`: Converts a text position to line/column numbers.
*   `table.appendArray(a, b)`: Appends array `b` to array `a`.
*   `table.unique(array)`: Returns unique elements from an array.
*   `table.uniqueKVBy(array, keyFn)`: Returns unique key-value pairs based on a key function.
*   `table.mergeKV(t1, t2)`: Merges two tables (recursive for nested tables).
*   `table.map(t, fn)`: Applies a function to each element of an array.
*   `table.toMd(data)`: Converts a table (or JSON) to a Markdown table.

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
-- priority: 20
mls=mls or {}

-- Convert meeting note title
-- Extracts the meeting title from the current page URL.
-- Assumes the URL format is like "namespace/Meeting_Note Title".
-- Splits the URL by "/", takes the last part, and then splits that by "_"
-- to remove the "Meeting" prefix and joins the remaining parts with a space.
function mls.getmeetingTitle()
  local t=string.split(string.split(editor.getCurrentPage(),"/")[#string.split(editor.getCurrentPage(),"/")],"_")
  table.remove(t,1)
  t=table.concat(t, " ")
  return t
end

-- Embed external resources
-- Creates an HTML iframe to embed an external URL within the current page.
-- Allows specifying width and height, defaulting to "100%" and "400px" respectively.
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
-- Recursively prints a Lua value, handling tables with indentation.
-- Prevents infinite recursion by limiting the depth to 5.
local function dump(value, depth)
  --print("[DEBUG][TYPE]"..type(value)) -- commented out debug line
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


-- Debug function
-- Prints a debug message to the console if LOG_ENABLE is true.
-- Uses the dump function to pretty-print the message.
-- Allows specifying a prefix for the debug message.
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
-- Helper function to find a child node of a given type within a parent node.
local getChild = function(node, type)
  for _, child in ipairs(node.children) do
    if child.type == type then
      return child
    end
  end
end

-- Get text of Node
-- Helper function to recursively extract the text content from a node.
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
-- Recursively searches for a code block (FencedCode node) with a specific blockId in the node's children.
local findMyFence = function(node,blockId)
    if not node.children then
      return nil
    end
    for _, child in ipairs(node.children) do
        --mls.debug(child) -- commented out debug line
        if child.type == "FencedCode" then
          local info = getText(getChild(child, "CodeInfo"))
          --mls.debug(info) -- commented out debug line
          if info  and info:find(blockId) then
            mls.debug(info)
            return getChild(child, "CodeText")
          end
        end
        local result= findMyFence(child,blockId)
        if result ~=nil then
          return result
        end
      --break --  for loop
    end --for
end

-- Get code source in md codeblock
-- Parses a Markdown page, finds a code block with the given blockId, and returns its content.
-- Allows replacing a token within the code block with a new text value.
function mls.getCodeBlock  (page,blockId,token,text)
  local tree = markdown.parseMarkdown(space.readPage(page))
  --mls.debug(tree) -- commented out debug line
  if tree then
    local fence = findMyFence(tree,blockId)
    --mls.debug(fence) -- commented out debug line
    if fence then
      local result=fence.children[1].text
      if token == nil or text==nil then
        return result
      else
        return string.gsub(result, token, text)
      end
    end
  end
  return "Error"
end

-- Parse ISO Date
-- Parses an ISO date string into a Unix timestamp.
-- This function appears incomplete and has a potential error in the offset calculation.
-- The `xoffset` variable is not defined.
function mls.parseISODate(isoDate)
    local pattern = "(%d+)%-(%d+)%-(%d+)%a(%d+)%:%d+:%d+([Z%+%-])(%d?%d?)%:?(%d?%d?)"
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

-- Get Stdlib Internal
-- Retrieves a list of internal API keys from a remote file.
-- Caches the results to avoid repeated fetching.
-- The URL points to a file in the silverbulletmd/silverbullet repository.
function mls.getStdlibInternal()
  if _G ~=nil then
    return table.keys(_G)
  end 
  -- get list of internal api TODO: remove
  local KEY="stdlib_internal"
  local result=mls.cache.ttl.CacheManager.get(KEY)
  if  result == nil then 
    local url = "https://raw.githubusercontent.com/silverbulletmd/silverbullet/refs/heads/main/client/space_lua/stdlib.ts"  
    local resp = net.proxyFetch(url)   
    if resp.status ~= 200 then  
      error("Failed to fetch file: " .. resp.status)  
    end  
    local content = resp.body  
    local results = {}   
    for line in string.split(content,"\n") do  
      local key = string.match(string.trim(line), 'env%.set%("(.*)"')  
      if key  then  
        table.insert(results, key)  
      end
    end  
    result=table.sort(results)
    mls.cache.ttl.CacheManager.set(KEY,result)
  end  
  return table.sort(result)
end

-- Position to Line Column
-- Converts a character position within a text string to a line and column number.
function mls.positionToLineColumn(text, pos)  
  local line = 1  
  local column = 0  
  local lastNewline = -1  
    
  for i = 0, pos - 1 do  
    if string.sub(text, i + 1, i + 1) == "\n" then  
      line = line + 1  
      lastNewline = i  
      column = 0  
    else  
      column = column + 1  
    end  
  end  
    
  return { line = line, column = column }  
end

-----------------------------------------
-- TABLE
-----------------------------------------
-- Append Array
-- Appends all elements from one array to another.
function table.appendArray(a, b)
    if a~= nil and b ~= nil then
      for i = 1, #b do
          table.insert(a, b[i])
      end
    end
    return a
end

-- Unique
-- Returns a new array containing only the unique elements from the input array.
function table.unique(array)
    local seen = {}
    local result = {}

    for i = 1, #array do
        local v = array[i]
        if not seen[v] then
            seen[v] = true
            result[#result + 1] = v
        end
    end

    return result
end

-- Unique KV By
-- Returns a new array containing only the unique key-value pairs from the input array,
-- based on a provided key function.
function table.uniqueKVBy(array, keyFn)
    local seen = {}
    local result = {}

    for i = 1, #array do
        local key = keyFn(array[i])
        if not seen[key] then
            seen[key] = true
            result[#result + 1] = array[i]
        end
    end

    return result
end

-- Merge KV
-- Merges two tables, recursively merging nested tables.
-- If a key exists in both tables and the values are both tables, the nested tables are merged.
-- Otherwise, the value from the second table overwrites the value from the first table.
function  table.mergeKV(t1, t2)
    for k, v in pairs(t2) do
        if type(v) == "table" and type(t1[k]) == "table"  then
            mergeTablesRecursive(t1[k], v)
        else
            t1[k] = v
        end
    end
    return t1
end

-- Map
-- Applies a function to each element of an array and returns a new array with the results.
function table.map(t, fn)
  local result = {}
  for i, v in ipairs(t) do
    result[i] = fn(v, i)
  end
  return result
end

-- To Md
-- Converts a Lua table to a Markdown table string.
-- Handles both arrays of arrays and arrays of objects.
-- Can parse JSON or Lua strings as input.
function table.toMd(data)
    local tbl
    local input=string.trim(data)
    -- If input is a string, try parsing as JSON
    if string.startsWith(data,"{") then
      -- Lua
      tbl=spacelua.evalExpression(spacelua.parseExpression(data)) 
    else
      --JSON
      tbl=js.tolua(js.window.JSON.parse(js.tojs(data)))
    end  
    if #tbl == 0 then return "" end

    local md = {}

    -- Helper to convert a row to Markdown
    local function rowToMd(row)
        local cells = {}
        for _, cell in ipairs(row) do
            table.insert(cells, tostring(cell))
        end
        return "| " .. table.concat(cells, " | ") .. " |"
    end

    -- Handle array of objects
    local first = tbl[1]
    local headers
    if type(first) == "table" and not (#first > 0) then
        headers = {}
        for k in pairs(first) do table.insert(headers, k) end
        local rows = {headers}
        for _, obj in ipairs(tbl) do
            local row = {}
            for _, h in ipairs(headers) do
                table.insert(row, obj[h] or "")
            end
            table.insert(rows, row)
        end
        tbl = rows
    end

    -- Header
    table.insert(md, rowToMd(tbl[1]))

    -- Separator
    local sep = {}
    for _ = 1, #tbl[1] do table.insert(sep, "---") end
    table.insert(md, "| " .. table.concat(sep, " | ") .. " |")

    -- Data rows
    for i = 2, #tbl do
        table.insert(md, rowToMd(tbl[i]))
    end

    return table.concat(md, "\n")
end
---- Events

```

## Changelog

* 2026-01-22:
  * getStdlibInternal compatible with edge version https://community.silverbullet.md/t/risk-audit/3562/14
* 2026-01-20:
  * feat: add table functions
    * map
    * mergeKV
    * uniqueKVBy
    * unique
    * appendArray
  * feat: add `mls.getStdlibInternal` function

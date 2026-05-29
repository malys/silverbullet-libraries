---
author: malys
description: Export md table to different formats (json,csv,yaml). 
pageDecoration.prefix: "🛠️ "
name: "Library/Malys/TableExport"
tags: meta/library
---
# Table export

## Description

Export selected md table to different formats:
* JSON
* YAML
* CSV

## Commands

- **Table: Export**: Copies the table data to your clipboard in the chosen format.

## Code
```space-lua
local function exportTable(rows, format,limit)  
  if not rows or #rows == 0 then  
    editor.flashNotification("No table rows to export", "error")  
    return  
  end  
  if limit and limit > 0 then
    local truncated = {}
    for i = 1, math.min(limit, #rows) do
      table.insert(truncated, rows[i])
    end
    rows = truncated
  end

  local cleanRows = {}  
  for _, row in ipairs(rows) do  
    local cleanRow = {}  
    for k, v in pairs(row) do  
      if k ~= "ref" and k ~= "tag" and k ~= "range" and k ~= "tags" and k ~= "page" and k ~= "pos" and k ~= "tableref" then  
        cleanRow[k] = v  
      end  
    end  
    table.insert(cleanRows, cleanRow)  
  end  

  local export = ""  

  if format == "json" then  
    export = js.window.JSON.stringify(js.tojs(cleanRows))  

  elseif format == "csv" then  
    local SEP = ";"  
    local headers = {}  
    for k, _ in pairs(cleanRows[1]) do  
      table.insert(headers, k)  
    end  

    export = table.concat(headers, SEP) .. "\n"  

    for _, row in ipairs(cleanRows) do  
      local vals = {}  
      for _, h in ipairs(headers) do  
        local v = tostring(row[h] or ""):gsub('"', '""')  
        if v:find("[" .. SEP .. "\n\"]") then v = '"' .. v .. '"' end  
        table.insert(vals, v)  
      end  
      export = export .. table.concat(vals, SEP) .. "\n"  
    end  

  elseif format == "yaml" then  
    export = yaml.stringify(cleanRows)  

  elseif format == "api" then
    local apiUrl = editor.prompt("API endpoint")
    if not apiUrl then return end
  
    local payload = js.window.JSON.stringify(js.tojs(cleanRows))
  
    local response = http.request(apiUrl, {
      method = "POST",
      headers = {
        ["Content-Type"] = "application/json",
        ["Accept"] = "application/json"
      },
      body = payload
    })
  
    if response.status >= 200 and response.status < 300 then
      editor.flashNotification("Table sent to API")
    else
      editor.flashNotification("API error: " .. tostring(response.status), "error")
    end
  
    return

  else  
    editor.flashNotification("Unsupported format: " .. tostring(format), "error")  
    return  
  end  

  editor.copyToClipboard(export)  
  editor.flashNotification("Copied table as " .. format)  
end
-- Helper to find which table contains the cursor position  
local function findTableAtCursor(rows, cursorPos)  
  local currentTableref = nil  
  for _, row in ipairs(rows) do  
    if row.pos <= cursorPos then  
      currentTableref = row.tableref  
    else  
      break  
    end  
  end  
  return currentTableref  
end  
  
-- Updated export command with cursor-aware filtering  
command.define {  
  name = "Table: export",  
  run = function()  
    local cursorPos = editor.getCursor()  
    local rows = query[[from index.tag "table" where page == editor.getCurrentPage() order by pos]]  
    local targetTableref = findTableAtCursor(rows, cursorPos)  
      
    if not targetTableref then  
      editor.flashNotification("Cursor not inside a table", "error")  
      return  
    end  
      
    -- Filter rows to only include those from the table at cursor  
    local filteredRows = {}  
    for _, row in ipairs(rows) do  
      if row.tableref == targetTableref then  
        table.insert(filteredRows, row)  
      end  
    end  
      
    local format = editor.filterBox("Format", {    
      { name = "JSON", value = "json" },  
      { name = "YAML", value = "yaml" },  
      { name = "CSV", value = "csv" },
      { name = "POST to API", value = "api" }  
    }, "🔍 Select a format", "Type to search...")
      
    if format then
      local limit = nil
      if format.value ~= "api" then
        local nStr = editor.prompt("First N rows to export (leave empty = all)")
        if nStr and nStr ~= "" then
          limit = tonumber(nStr)
          if not limit or limit < 1 then
            editor.flashNotification("Invalid N, exporting all rows", "warning")
            limit = nil
          end
        end
      end
      exportTable(filteredRows, format.value, limit)
    end
  end  
}
```

## Changelog

* 2026-02-28:
  * feat: support json,csv,yaml format to export
 
## Community

[Silverbullet forum](https://community.silverbullet.md/t/risk-audit/3562)



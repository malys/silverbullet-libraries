---
author: malys
description:  Integrate FormulaJS in markdown table (table = sheet).
name: "Library/Malys/MdTableSheet"
tags: meta/library
---
# Md Table + Formulajs evaluator

This feature allows you to embed dynamic formulas in your Markdown tables. You can use the \`F\` function to evaluate formulas and display their results in your tables.

The \`F\` function takes two arguments:
- \`formulajs\`: The formula to evaluate using the Formulajs library.
- \`label\` (optional): A label to differentiate between the same formula in different tables.

Here's an example usage: \${F("SUM(A1:A5)","1")}\`


| Header A | Header B |
| --- | --- |
| 1.2 | 2   |
| 3   | 4   |
| 5   | 6   |
| 7   | 8   |
| 9   | 10  |
| ${F("CONCAT(A1,A2)")} | ${F("SUM(A1:B5)")} |


| Header A | Header B | H5  |
| --- | --- | --- |
| 10  | 20  | 50  |
| 30  | 40  | 50  |
| 50  | 60  | 50  |
| 70  | 80  | 50  |
| 90  | 100 | 50  |
| ${F("SUM(A1:B5)","1")} | ${F("SUM(B1:B5)","2")} | ${F("AVERAGE(C1:C5)","2")} |



```space-lua
-- ---------------------------
-- SilverBullet Markdown Table + Formulajs evaluator
-- Use: F(formulajs,label)
-- label is optional but necessary if differenciate same formula is different table
-- Example: ${F("SUM(A1:A5)","1")}

-- Instructions to generate space lua scripts for silverbullet https://silverbullet.md
-- every function must be surrounded by debug_log (not only main)
-- **not use lua standard methods but space-lua silverbullet api (https://silverbullet.md/API)** Be sure to use same function signature
-- [asset](https://silverbullet.md/API/asset)
-- [clientStore](https://silverbullet.md/API/clientStore)
-- [codeWidget](https://silverbullet.md/API/codeWidget)
-- [command](https://silverbullet.md/API/command)
-- [config](https://silverbullet.md/API/config)
-- [datastore](https://silverbullet.md/API/datastore)
-- [editor](https://silverbullet.md/API/editor)
-- [encoding](https://silverbullet.md/API/encoding)
-- [event](https://silverbullet.md/API/event)
-- [global](https://silverbullet.md/API/global)
-- [http](https://silverbullet.md/API/http)
-- [index](https://silverbullet.md/API/index)
-- [js](https://silverbullet.md/API/js)
-- [jsonschema](https://silverbullet.md/API/jsonschema)
-- [language](https://silverbullet.md/API/language)
-- [lua](https://silverbullet.md/API/lua)
-- [markdown](https://silverbullet.md/API/markdown)
-- [math](https://silverbullet.md/API/math)
-- [mq](https://silverbullet.md/API/mq)
-- [os](https://silverbullet.md/API/os)
-- [shell](https://silverbullet.md/API/shell)
-- [slashCommand](https://silverbullet.md/API/slashCommand)
-- [space](https://silverbullet.md/API/space)
-- [spacelua](https://silverbullet.md/API/spacelua)
-- [string](https://silverbullet.md/API/string)
-- [sync](https://silverbullet.md/API/sync)
-- [system](https://silverbullet.md/API/system)
-- [table](https://silverbullet.md/API/table)
-- [template](https://silverbullet.md/API/template)
-- [yaml](https://silverbullet.md/API/yaml)
-- IMPORTANT: use string.split(s, sep) instead of s:split() to avoid JS/Lua interop issues
-- make code syntax simple, **safe** and easy debugable (during the pediod of development functions are public and at the end, switch to local function by default)
-- ---------------------------


local LOG_ENABLE = false
function debug_log(message)
  if LOG_ENABLE then
    local log_message = ""
    if type(message) == "table" then
      log_message = tostring(message)
    else
      -- Assume it's a string, number, boolean, or nil
      log_message = tostring(message)
    end
    
    js.log("[DEBUG] " .. log_message)
  end
end

-- Import Formulajs
local formulajs = js.import("https://esm.sh/@formulajs/formulajs")

-- =========================
-- Helper functions (kept only conversion helpers)
-- =========================

-- Convert column letters to number (A=1, B=2, ..., AA=27)
function colToNumber(col)
  local n = 0
  for i = 1, string.len(col) do
    n = n * 26 + (string.byte(col, i) - string.byte("A") + 1)
  end
  return n
end

-- Convert number to column letters (1=A, 27=AA)
function numberToColLetters(c)
  local s = ""
  while c > 0 do
    local r = (c - 1) % 26
    s = string.char(r + 65) .. s
    c = math.floor((c - 1) / 26)
  end
  return s
end

-- =========================
-- Markdown table parsing / cell map (uses index for formula eval)
-- =========================

function expandRange(range, cellMap)
  debug_log("Expanding range: " .. range)
  local colStart, rowStart, colEnd, rowEnd = string.match(range, "([A-Z]+)(%d+):([A-Z]+)(%d+)")
  if not colStart then
    debug_log("Invalid range: " .. range)
    return {}
  end
  
  local sCol, eCol = colToNumber(colStart), colToNumber(colEnd)
  local sRow, eRow = tonumber(rowStart), tonumber(rowEnd)
  local vals = {}
  for r = sRow, eRow do
    for c = sCol, eCol do
      local key = numberToColLetters(c) .. r
      local v = cellMap[key]
      if v ~= nil then table.insert(vals, v) end
    end
  end
  debug_log("Expanded " .. range .. " into " .. tostring(#vals) .. " values")
  return vals
end

function extractTable(rows)
   local data = {}
   for _, row in ipairs(rows) do
      local rowData = {}
      local col = 1
      for k, v in pairs(row) do
         if k ~= "ref" and k ~= "tag" and k ~= "tags" and
              k ~= "itags" and k ~= "page" and k ~= "pos" and
              k ~= "tableref" then
            rowData[col] = v
            col = col + 1
         end
      end
      table.insert(data, rowData)
   end
   return data
end

function extractTables(pageName)
   if not pageName then pageName = editor.getCurrentPage() end
   debug_log("Extracting tables from page: " .. pageName)

   local allRows = query[[from index.tag "table" where page == pageName]]
   local tableGroups = {}
   for _, row in ipairs(allRows) do
      if not tableGroups[row.tableref] then tableGroups[row.tableref] = {} end
      table.insert(tableGroups[row.tableref], row)
   end

   local results = {}
   for tRef, rows in pairs(tableGroups) do
      results[tRef] = extractTable(rows)
   end
   debug_log("Extracted " .. tostring(#(allRows or {})) .. " table rows")
   return results
end

function toCellMap(tableData)
   local map = {}
   for r, row in ipairs(tableData) do
      for c, val in ipairs(row) do
         local key = numberToColLetters(c) .. r
         map[key] = tonumber(val) or val
      end
   end
   return map
end

function findTableOfFormula(pageName, formulaString, label)
   debug_log("Searching table for formula: " .. formulaString .. " / label=" .. (label or "nil"))
   if not pageName then pageName = editor.getCurrentPage() end
   local allRows = query[[from index.tag "table" where page == pageName]]
   local search = formulaString
   if label then search = '"' .. formulaString .. '","' .. label .. '"' end
   for _, row in ipairs(allRows) do
      for k, v in pairs(row) do
         if k ~= "ref" and k ~= "tag" and k ~= "tags" and
              k ~= "itags" and k ~= "page" and k ~= "pos" and
              k ~= "tableref" then
            if type(v) == "string" and string.find(v, search, 1, true) then
               debug_log("Formula found in table: " .. row.tableref)
               return row.tableref
            end
         end
      end
   end
   debug_log("Formula not found in any table")
   return nil
end

-- =========================
-- Formula evaluator
-- =========================

function F(formulaString, label, pageName)
   debug_log("Evaluating F: " .. formulaString .. " / label=" .. (label or "nil"))

   if not pageName then pageName = editor.getCurrentPage() end
   local tRef = findTableOfFormula(pageName, formulaString, label)
   if not tRef then return "ERROR: formula not in any table" end
   local tables = extractTables(pageName)
   local tbl = tables[tRef]
   if not tbl then return "ERROR: table not found" end
   local cellMap = toCellMap(tbl)

   local funcName = string.match(formulaString, "^(%w+)%(")
   local argsStr   = string.match(formulaString, "%((.*)%)")
   if not funcName then return "ERROR: invalid formula syntax" end

   debug_log("Function: " .. funcName .. " Args: " .. (argsStr or ""))

   local args = {}
   for a in string.gmatch(argsStr or "", "([^,]+)") do
      a = string.trim(a) -- Use string.trim
      if string.match(a, "^[A-Z]+%d+:[A-Z]+%d+$") then
         local vals = expandRange(a, cellMap)
         for _, v in ipairs(vals) do table.insert(args, v) end
      elseif string.match(a, "^[A-Z]+%d+$") then
         table.insert(args, cellMap[a])
      else
         table.insert(args, tonumber(a) or a)
      end
   end

   if not formulajs[funcName] then
      debug_log("Unknown function: " .. funcName)
      return "ERROR: unknown function " .. funcName
   end

   local status, result = pcall(function() return formulajs[funcName](table.unpack(args)) end)
   if not status then return "ERROR: " .. tostring(result) end

   debug_log("Formula result: " .. tostring(result))
   return result
end

-- =========================
-- Table helpers for editing (must use live text, not indexed data)
-- =========================

function isCursorInTable()
   local line = editor.getCurrentLine()
   if line == nil then
     line =false 
      return false
  end
   local result=string.match(line.text, "^%s*|.*|%s*$")
   if result == nil then 
       return false
   else 
    return true
   end
end

function getTableBlock()
   local lines = string.split(editor.getText(), "\n") 
   local cursorLine = editor.getCursor() or 1
   local startLine=cursorLine
   local endLine =  cursorLine
   local pointer=true
  
   while lines and #lines>2 and startLine > 1 and pointer do 
     pointer=string.match(lines[startLine - 1], "^%s*|.*|%s*$") 
     if pointer == nil then
       pointer=false
     else 
       pointer=true
     end
     startLine = startLine - 1 
   end
   pointer=true
   while lines and #lines>2 and endLine > 1 and pointer do 
     pointer=string.match(lines[endLine + 1], "^%s*|.*|%s*$") 
     if pointer == nil then
       pointer=false
     else 
       pointer=true
     end
     endLine = endLine + 1 
   end
   return  lines,startLine,endLine
end

function splitRow(line)
   local cells = {}
   for cell in string.gmatch(line, "|([^|]*)") do
      table.insert(cells, string.trim(cell)) 
   end
   return cells
end

function joinRow(cells)
   local out = {}
   for i = 1, #cells do out[i] = tostring(cells[i] or "") end
   debug_log(out)
   return "| " .. table.concat(out, " | ") .. " |" -- Use table.concat
end

function firstNonEmptyOffset(cellText)
   if not cellText or cellText == "" then return 1 end
   return string.find(cellText, "%S") or 1
end

function getCellAbsolutePosition(lines, lineIndex, colIndex)
    local line = lines[lineIndex] or ""
    local currentPos = 1 -- Start position in the string (1-indexed)
    local colCount = 0
    local pos = nil

    -- Find the first pipe, which usually starts the table
    local firstPipe = string.find(line, "|", currentPos)
    if not firstPipe then
        return (string.find(line, "|") or 1) + 1 -- Fallback logic
    end
    currentPos = firstPipe + 1

    -- Iterate through the cells until the target column is found
    while currentPos <= string.len(line) do
        -- Find the next pipe starting from currentPos
        local nextPipe = string.find(line, "|", currentPos)
        if not nextPipe then
            -- We've reached the end of the line
            break
        end

        colCount = colCount + 1

        -- Extract the cell content (text between currentPos and nextPipe)
        local cellText = string.sub(line, currentPos, nextPipe - 1)
        
        if colCount == colIndex then
            -- Calculate the absolute position:
            -- 1. nextPipe - string.len(cellText) is the index just before the cell's content starts.
            -- 2. Add firstNonEmptyOffset to find the first non-whitespace character.
            pos = (nextPipe - string.len(cellText)) + firstNonEmptyOffset(cellText) - 1
            break
        end

        -- Move to the position after the pipe for the next cell
        currentPos = nextPipe + 1
    end

    -- Return the calculated position, or fall back to the start of the first cell
    return pos or (string.find(line, "|") or 1) + 1
end

function withTableEdit(fn)
   if not isCursorInTable() then return end
   local lines, s, e = getTableBlock()
   fn(lines, s, e)
   editor.setText(table.concat(lines, "\n")) 
end

-- =========================
-- Cell Navigation (Ctrl+Arrow)
-- =========================

function moveCell(dx, dy)
   if not isCursorInTable() then return end
   local lines, s, e = getTableBlock()
   local cur = editor.getCursor()
   local relRow = cur.line - s + 1
   local rowText = lines[cur.line] or ""
   local colIndex = 1
   local acc = 0
   for i, cell in ipairs(splitRow(rowText)) do
      acc = acc + string.len(cell) + 3 -- Use string.len
      if acc >= cur.ch then colIndex = i break end
   end

   local targetRow, targetCol = relRow + dy, colIndex + dx
   if targetRow < 1 or targetRow > (e - s + 1) then return end
   local targetCells = splitRow(lines[s + targetRow - 1])
   if targetCol < 1 or targetCol > #targetCells then return end

   local newCh = getCellAbsolutePosition(lines, s + targetRow - 1, targetCol)
   editor.moveCursor({ line = s + targetRow - 1, ch = newCh })
end

-- =========================
-- Commands (all use correct syntax)
-- =========================

command.define { name="Table: Move Cell Left",   run=function() moveCell(-1,0) end }
command.define { name="Table: Move Cell Right", run=function() moveCell(1,0) end }
command.define { name="Table: Move Cell Up",      run=function() moveCell(0,-1) end }
command.define { name="Table: Move Cell Down",   run=function() moveCell(0,1) end }

command.define { name="Table: Add Column Right", run=function()
   withTableEdit(function(lines,s,e) for i=s,e do table.insert(splitRow(lines[i]), "") lines[i]=joinRow(splitRow(lines[i])) end end) -- Use table.insert
end}

command.define { name="Table: Add Row Bottom", run=function()
   withTableEdit(function(lines,s,e)
      local cells = splitRow(lines[e])
      local newRow = {}
      for _=1,#cells do table.insert(newRow,"") end -- Use table.insert
      table.insert(lines,e+1,joinRow(newRow)) -- Use table.insert
   end)
end}

command.define { name="Table: Remove Row", run=function()
   withTableEdit(function(lines,s,e) local cur=editor.getCursor().line; if cur>=s and cur<=e then table.remove(lines,cur) end end) -- Use table.remove
end}

command.define { name="Table: Remove Column", run=function()
   withTableEdit(function(lines,s,e)
      local cur = editor.getCursor()
      local row = splitRow(lines[cur.line])
      local colIndex = 1
      local acc = 0
      for i, cell in ipairs(row) do acc=acc+string.len(cell)+3 if acc>=cur.ch then colIndex=i break end end -- Use string.len
      for i=s,e do local cells=splitRow(lines[i]); table.remove(cells,colIndex); lines[i]=joinRow(cells) end -- Use table.remove
   end)
end}

command.define { name="Table: Move Row Up", run=function()
   withTableEdit(function(lines,s,e)
      local cur=editor.getCursor().line
      if cur>s then lines[cur],lines[cur-1]=lines[cur-1],lines[cur] end
   end)
end}

command.define { name="Table: Move Row Down", run=function()
   withTableEdit(function(lines,s,e)
      local cur=editor.getCursor().line
      if cur<e then lines[cur],lines[cur+1]=lines[cur+1],lines[cur] end
   end)
end}

command.define { name="Table: Move Column Left", run=function()
   withTableEdit(function(lines,s,e)
      local cur=editor.getCursor().line
      local row=splitRow(lines[cur])
      local colIndex=1
      local acc=0
      for i,cell in ipairs(row) do acc=acc+string.len(cell)+3 if acc>=editor.getCursor().ch then colIndex=i break end end -- Use string.len
      if colIndex>1 then for i=s,e do local cells=splitRow(lines[i]); cells[colIndex],cells[colIndex-1]=cells[colIndex-1],cells[colIndex]; lines[i]=joinRow(cells) end end
   end)
end}

command.define { name="Table: Move Column Right", run=function()
   withTableEdit(function(lines,s,e)
      local cur=editor.getCursor().line
      local row=splitRow(lines[cur])
      local colIndex=1
      local acc=0
      for i,cell in ipairs(row) do acc=acc+string.len(cell)+3 if acc>=editor.getCursor().ch then colIndex=i break end end -- Use string.len
      for i=s,e do local cells=splitRow(lines[i]); if colIndex<#cells then cells[colIndex],cells[colIndex+1]=cells[colIndex+1],cells[colIndex] end; lines[i]=joinRow(cells) end
   end)
end}

command.define { name="Table: Transpose Rows and Columns", run=function()
   withTableEdit(function(lines,s,e)
      local data={}
      for i=s,e do table.insert(data,splitRow(lines[i])) end -- Use table.insert
      local transposed={}
      for c=1,#data[1] do local newRow={} for r=1,#data do table.insert(newRow,data[r][c] or "") end; table.insert(transposed,joinRow(newRow)) end -- Use table.insert
      for i=0,(e-s) do lines[s+i]=transposed[i+1] or "" end
   end)
end}

command.define { name="Table: Sort Column Ascending", run=function()
   withTableEdit(function(lines,s,e)
      local header=table.remove(lines,s) -- Use table.remove
      local rows={}
      for i=s,e-1 do table.insert(rows,splitRow(lines[i])) end -- Use table.insert
      local curRow=splitRow(lines[editor.getCursor().line])
      local colIndex=1; local acc=0
      for i,cell in ipairs(curRow) do acc=acc+string.len(cell)+3 if acc>=editor.getCursor().ch then colIndex=i break end end -- Use string.len
      table.sort(rows,function(a,b) return (a[colIndex] or "")<(b[colIndex] or "") end)
      for i=0,#rows-1 do lines[s+i]=joinRow(rows[i+1]) end
      table.insert(lines,s,header) -- Use table.insert
   end)
end}

command.define { name="Table: Sort Column Descending", run=function()
   withTableEdit(function(lines,s,e)
      local header=table.remove(lines,s) -- Use table.remove
      local rows={}
      for i=s,e-1 do table.insert(rows,splitRow(lines[i])) end -- Use table.insert
      local curRow=splitRow(lines[editor.getCursor().line])
      local colIndex=1; local acc=0
      for i,cell in ipairs(curRow) do acc=acc+string.len(cell)+3 if acc>=editor.getCursor().ch then colIndex=i break end end -- Use string.len
      table.sort(rows,function(a,b) return (a[colIndex] or "")>(b[colIndex] or "") end)
      for i=0,#rows-1 do lines[s+i]=joinRow(rows[i+1]) end
      table.insert(lines,s,header) -- Use table.insert
   end)
end}
```


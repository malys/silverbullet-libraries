---
author: malys
description:  Integrate FormulaJS in markdown table (table = sheet).
pageDecoration.prefix: "🛎️ "
name: "Library/Malys/MdTableSheet"
tags: meta/library
---
# Md Table 

## Disclaimer & Contributions

This code is provided **as-is**, **without any kind of support or warranty**.  
I do **not** provide user support, bug-fixing on demand, or feature development.

If you detect a bug, please **actively participate in debugging it** (analysis, proposed fix, or pull request) **before reporting it**. Bug reports without investigation may be ignored.

🚫 **No new features will be added.**  
✅ **All types of contributions are welcome**, including bug fixes, refactoring, documentation improvements, and optimizations.

By using or contributing to this project, you acknowledge and accept these conditions.


## Formulajs evaluator

![](https://community.silverbullet.md/uploads/default/original/2X/2/2331d5ffb379c3209dc7c0b1065283137f873d72.gif)

This feature allows you to embed dynamic formulas in your Markdown tables. You can use the \`F\` local function to evaluate formulas and display their results in your tables.

The \`F\` local function takes two arguments:
- \`formulajs\`: The formula to evaluate using the [Formulajs](https://formulajs.info/functions/) library.
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

### Supported functions

Every function in [list](https://formulajs.info/functions/) is in theory supported.

But, I have tested only:
* AVERAGE
* CONCAT
* SUM
* SUMIF
  
## ChartJS (online)

![](https://community.silverbullet.md/uploads/default/original/2X/a/a79eebba75448fb6f9a1890855b683a4a9b8c282.gif)

This feature allows you to embed interactive charts in your Markdown tables using ChartJS library. You can use the `G` local function to create charts and display them in your tables.

The `G` local function takes four arguments:

- `label` (mandatory, unique id of chart): A label to differentiate between the same chart in different tables.
- `pageName` (optional): The name of the page where the chart should be displayed. If not provided, the current page will be used.
- `XRange`: The range of cells to use for the X-axis.
- `YRange`: The range of cells to use for the Y-axis.
- `options` (optional): An object containing additional options for the chart. (width, height,serieLabel, options: [chartjs options](https://quickchart.io/documentation))

Here's an example usage: \${G("MyChart", "Page 1", "A1:A5", "B1:B5", { type= "line", w= 400, h= 600, serieLabel= "Series 1", options={
    spanGaps= false,
    elements= {
      line= {
        tension= 0.000001
      }
    }, 
    scale={
     gridLines={
       color= "lightgrey",
       lineWidth= 0.1
     },
     angleLines={
       color= "lightgrey",
       lineWidth= 0.1
     },
     pointLabels={
        display= true,
        fontSize= 10,
        fontStyle= "normal",
        fontColor= "lightgrey"
     },
      ticks = {
        showLabelBackdrop=false,
        padding=10,
        fontColor= "lightgrey",
        display = true,
        min= 0,  
        max= 10,
      }
    }
  })}

Here's an example chart:

| Header A | Header B |
| --- | --- |
| 1.2 | 2   |
| 3   | 4   |
| 5   | 6   |
| 7   | 8   |
| 9   | 10  |
| 9   | 10  |

${G("2","","A1:A3","B1:B3",{type="line", serieLabel="Example",width=300,height=80})}
${G("2","","A1:A3",{"B4:B6","B1:B3"},{type="line", serieLabel={"A","B"},width=300,height=80})}
### Supported features
* single charts
* series
* customization with chartjs options
  
## Table inserts

*   **Table: Insert line below** \- Inserts a new line below the current cursor position in a table format, matching the number of pipes ("|") in the current line. (Shortcut: `Alt--`)
*   **Table: Insert column** \- Inserts a new column into the table at the position of the nearest pipe ("|") to the cursor, affecting the current line and subsequent table rows. (Shortcut: `Alt-+`)
*   
![](https://community.silverbullet.md/uploads/default/original/2X/e/ec9b8a44f48b1854b94544da609e24fb1c9bf888.gif)

## Code source


```space-lua
-- luacheck: globals G F 
-- ---------------------------
-- SilverBullet Markdown Table + Formulajs evaluator
-- Use: F(formulajs,label)
-- label is optional but necessary if differenciate same formula is different table
-- Example: ${F("SUM(A1:A5)","1")}

-- Instructions to generate space lua scripts for silverbullet https://silverbullet.md
-- every local function must be surrounded by log (not only main)
-- **not use lua standard methods but space-lua silverbullet api (https://silverbullet.md/API)** Be sure to use same local function signature
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
mls = mls or {}
mls.table = mls.table or {}

local function log(...)
  if LOG_ENABLE and mls and mls.debug then
     if type(mls.debug) == "function" then 
       mls.debug(table.concat({...}, " "))
     end  
  end
end

-- Import Formulajs
local formulajs = js.import("https://esm.sh/@formulajs/formulajs")

-- =========================
-- Helper functions (kept only conversion helpers)
-- =========================

-- Convert column letters to number (A=1, B=2, ..., AA=27)
local function colToNumber(col)
  local n = 0
  for i = 1, string.len(col) do
    n = n * 26 + (string.byte(col, i) - string.byte("A") + 1)
  end
  return n
end

-- Convert number to column letters (1=A, 27=AA)
local function numberToColLetters(c)
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

local function expandRange(range, cellMap)
  log("Expanding range: " .. range)
  local colStart, rowStart, colEnd, rowEnd = string.match(range, "([A-Z]+)(%d+):([A-Z]+)(%d+)")
  if not colStart then
    log("Invalid range: " .. range)
    return {}
  end
   log("Expanding range: " .. colStart.." ".. rowStart.." ".. colEnd.." ".. rowEnd)
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
  log("Expanded " .. range .. " into " .. tostring(#vals) .. " values")
  return vals
end

-- Expand a single cell range, e.g. A1 or A1:B2
-- This local function is used when a cell range is not given, e.g. F(A1)
-- In this case, the range is A1:A1

local function extractTable(rows)
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

-- Returns a table of tables where each inner table is a row in the table.
-- Inner tables are dictionaries where keys are column numbers and values are cell values.
--
-- Example usage:
--
-- local tables = extractTables('Page 1')
-- for _, table in ipairs(tables) do
--    for _, row in ipairs(table) do
--       for column, value in pairs(row) do
--          print(column, value)
--       end
--    end
-- end

local function extractTables(pageName)
   if not pageName then pageName = editor.getCurrentPage() end
   log("Extracting tables from page: " .. pageName)

   local allRows = query[[from index.tag "table" where page == pageName order by pos]]
   local tableGroups = {}
   for _, row in ipairs(allRows) do
      if not tableGroups[row.tableref] then tableGroups[row.tableref] = {} end
      table.insert(tableGroups[row.tableref], row)
   end

   local results = {}
   for tRef, rows in pairs(tableGroups) do
      results[tRef] = extractTable(rows)
   end
   log("Extracted " .. tostring(#(allRows or {})) .. " table rows")
   return results
end

-- Returns a dictionary where keys are cell addresses (e.g. "A1", "B2") and values are cell values.
--
-- Example usage:
--
-- local cellMap = toCellMap(extractTables('Page 1')[1])
-- for cellAddress, value in pairs(cellMap) do
--    print(cellAddress, value)
-- end

local function toCellMap(tableData)
   local map = {}
   for r, row in ipairs(tableData) do
      for c, val in ipairs(row) do
         local key = numberToColLetters(c) .. r
         map[key] = tonumber(val) or val
      end
   end
   return map
end

-- Returns the table that contains the given formula.
-- If no table is found, returns nil.
--
-- Example usage:
--
-- local table = findTableOfFormula('Page 1', 'SUM(A1:A5)')
-- if table then
--    print(table)
-- end

local function findTableOfFormula(pageName, formulaString, label)
   log("Searching table for formula: " .. formulaString .. " / label=" .. (label or "nil"))
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
               log("Formula found in table: " .. row.tableref)
               return row.tableref
            end
         end
      end
   end
   log("Formula not found in any table")
   return nil
end

---
-- Finds the position of a pattern in a page.
--
-- @param pageName string - The name of the page to search.
-- @param pattern string - The pattern to search for.
-- @return number - The position of the first occurrence of the pattern, or nil if not found.

local function findPosition(pageName, pattern)
   if not pageName or pageName == "" then
      pageName = editor.getCurrentPage()
   end

   log("findPosition: loading page " .. tostring(pageName) .. " and searching for pattern "..pattern)

   local page = space.readPage(pageName)
   if not page then
      log("findPosition: page not found or has no text")
      return nil
   end

   local s, e = string.find(page, pattern, 1, true)
   if not s then
      log("findPosition: pattern not found")
      return nil
   end

   log("findPosition: pattern found at position " .. tostring(s) .. "-" .. tostring(e))
   return s
end

---
-- Extract formula name.
--
-- @param formula string.
local function extractFormula(formulaString)
 return string.match(formulaString, "^(%w+)%(")
end
---
-- Extract formula arguments.
--
-- @param formula string.
local function extractArgsFormula(formulaString)
   return string.match(formulaString, "%((.*)%)")
end
-- =========================
-- Formula evaluator
-- =========================

function F(formulaString, label, pageName)
   log("Evaluating F: " .. formulaString .. " / label=" .. (label or "nil"))

   if not pageName then pageName = editor.getCurrentPage() end
   local tRef = findTableOfFormula(pageName, formulaString, label)
   if not tRef then return "ERROR: formula not in any table" end
   local tables = extractTables(pageName)
   local tbl = tables[tRef]
   if not tbl then return "ERROR: table not found" end
   local cellMap = toCellMap(tbl)

   local funcName =extractFormula(formulaString)
   local argsStr   = extractArgsFormula(formulaString)
   if not funcName then return "ERROR: invalid formula syntax" end

   log("Function: " .. funcName .. " Args: " .. (argsStr or ""))

   local args = {}
   for a in string.gmatch(argsStr or "", "([^,]+)") do
      a = string.trim(a) -- Use string.trim
      if string.match(a, "^[A-Z]+%d+:[A-Z]+%d+$") then
         local vals = expandRange(a, cellMap)
         local tmp={}
         for _, v in ipairs(vals) do table.insert(tmp, v) end
         table.insert(args, tmp)
      elseif string.match(a, "^[A-Z]+%d+$") then
         table.insert(args, cellMap[a])
      else
         table.insert(args, tonumber(a) or a)
      end
   end

   if not formulajs[funcName] then
      log("Unknown function: " .. funcName)
      return "ERROR: unknown local function " .. funcName
   end
   log("local function after: " .. funcName .. " Args: " .. (table.concat(args," ") or ""))
   local status, result = pcall(function() return formulajs[funcName](table.unpack(args)) end)
   if not status then return "ERROR: " .. tostring(result) end

   log("Formula result: " .. tostring(result))
   return result
end

-- =========================
-- Table helpers for editing (must use live text, not indexed data)
-- =========================



---
-- Returns true if the cursor is currently inside a table.
-- @return boolean
-- @see isCursorInTable
---

local function isCursorInTable()
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

---
-- Returns the block of text that contains the cursor.
-- @return string
-- @see getTableBlock
---
local function getTableBlock()
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

---
-- Splits a row into cells.
-- @param line string
-- @return table
---
local function splitRow(line)
   local cells = {}
   for cell in string.gmatch(line, "|([^|]*)") do
      table.insert(cells, string.trim(cell)) 
   end
   while #cells > 0 and (cells[#cells] == nil or string.trim(cells[#cells]) == "") do
      table.remove(cells)
   end

   return cells
end

---
-- Joins a row of cells into a single string.
-- @param cells table
-- @return string
---
local function joinRow(cells)
   local out = {}
   for i = 1, #cells do out[i] = tostring(cells[i] or "") end
   log(out)
   return "| " .. table.concat(out, " | ") .. " |" -- Use table.concat
end

---
-- Returns the offset of the first non-empty character in a cell.
-- @param cellText string
-- @return number
---
local function firstNonEmptyOffset(cellText)
   if not cellText or cellText == "" then return 1 end
   return string.find(cellText, "%S") or 1
end

---
-- Returns the absolute position of a cell in a table.
-- @param lines table
-- @param lineIndex number
-- @param colIndex number
-- @return number
---
local function getCellAbsolutePosition(lines, lineIndex, colIndex)
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

---
-- Expands a single cell range into a list of values.
-- @param rangeStr string
-- @param cellMap table
-- @return table
---
local function expandSingleRange(rangeStr,cellMap)
    local dest = {}
    log("expandSingleRange: start")
    log(rangeStr)
    if not rangeStr or rangeStr == "" then
        return dest
    end
    rangeStr = string.upper(rangeStr)

    if string.match(rangeStr, "^[A-Z]+%d+:[A-Z]+%d+$") then
        log("expandSingleRange: 1")
        local vals = expandRange(rangeStr, cellMap)
        for _, v in ipairs(vals) do
            log(_,v)
            table.insert(dest, v)
        end
    elseif string.match(rangeStr, "^[A-Z]+%d+$") then
        log("expandSingleRange: 2")
        local v = cellMap[rangeStr]
        if v ~= nil then
            log(v) 
            table.insert(dest, v)
        end
    else
        table.insert(dest, rangeStr)
    end
    log("expandSingleRange: end")
    return dest
end

---
-- Edits a table in place.
-- @param fn function
---
local function withTableEdit(fn)
   if not isCursorInTable() then return end
   local lines, s, e = getTableBlock()
   fn(lines, s, e)
   editor.setText(table.concat(lines, "\n")) 
end

-- =========================
-- Cell Navigation (Ctrl+Arrow)
-- =========================

---
-- Moves the cursor to the specified cell.
-- @param dx number
-- @param dy number
---
local function moveCell(dx, dy)
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

-- TODO add commands


-- =========================
-- Chartjs
-- =========================

-- QuickChart configuration table
local quickchart = {}

-- Define configurable QuickChart settings
config.define("quickchart", {
  type = "object"
})

-- Initialize QuickChart base URL from config with a sensible default
local qc = config.get("quickchart") or ""
if qc == "" then
  quickchart.baseUrl = "https://quickchart.io"
  quickchart.version = "2.9.4"
else
  local cfg = config.get("quickchart") or {}
  local baseUrl = cfg.baseUrl or "https://quickchart.io"
  if string.endsWith(baseUrl, "/") then
    baseUrl = string.sub(baseUrl, 1, string.len(baseUrl) - 1)
  end
  quickchart.baseUrl = baseUrl
  quickchart.version = cfg.version or "2.9.4"
end


-- Validate that the given value is an array-like table
local function validate_series(xValues, yValues)
  log("validate_series: start")

  local ok = true
  local message = ""

  if type(xValues) ~= "table" then
    ok = false
    message = "xValues must be an array (table)"
  elseif type(yValues) ~= "table" then
    ok = false
    message = "yValues must be an array (table)"
  else
    local xLen = 0
    for _ in ipairs(xValues) do
      xLen = xLen + 1
    end

    local yLen = 0
    for _ in ipairs(yValues) do
      yLen = yLen + 1
    end

    if xLen == 0 then
      ok = false
      message = "xValues must not be empty"
    elseif yLen == 0 then
      ok = false
      message = "yValues must not be empty"
    elseif xLen ~= yLen then
      ok = false
      message = "xValues and yValues must have the same length!"
    end
  end

  log("validate_series: end - ok=" .. tostring(ok))
  return ok, message
end

local function build_chart_dataset(data, label)
  return {
    label = label,
    data = data,
    fill = false
  }
end
  
-- Build the Chart.js config as a Lua table (later converted with js.stringify)
local function build_chart_config(xValues, yValues, chartType,serieLabels,option)
  local options= option or {
    responsive=true,
    legend= {
        position="right"
    }
  }
  
  local datasets={}
  for i,l  in ipairs(serieLabels) do
    table.insert(datasets,build_chart_dataset(yValues[i],l))
  end
  
  log("build_chart_config: start")

  local t = chartType
  if t == nil or t == "" then
    t = "line"
  end

  local config = {
    type = t,
    data = {
      labels = xValues,
      datasets = datasets
    },
    options= options
  }

  log("build_chart_config: end")
  return config
end

local function getClosestTable(label,pageName,tables)
   log("getClosestTable: start")
   functionPosition=tonumber(findPosition(pageName, 'G("'..label..'"'))

   local minDiff = 100000
   local nearestTable
   for _, t in pairs(tables) do
      nearestTable = t
      break
   end
   for k,v in pairs(tables) do
      local tablePosition = tonumber(string.match(k, "@([0-9]+)")) or 0
      log("getClosestTable: tablePosition "..tablePosition)
      local diff = functionPosition - tablePosition
      if diff >= 0 and diff < minDiff and v ~= nil then
         log("getClosestTable: diff "..diff)
         minDiff = diff
         nearestTable = v
      end
   end

   if nearestTable then
      log("getClosestTable: found ")
      log(nearestTable)
      return nearestTable
   end
   log("getClosestTable: end")
end

---
-- Returns the HTML for the chart.
-- @param xValues table
-- @param yValues table
-- @param chartType string
-- @param serieLabel string
-- @param w number
-- @param h number
-- @return string
---
local function getHtml(xValues, yValues, chartType,serieLabels, w, h, options)
  log("getHtml: start")

  if #serieLabels~= #yValues and #serieLabels~= #xValues and  #yValues~= #xValues then
    log("G: number of series not the same")
    return "Number of series are not the same!"
  end

  for i,x in ipairs(yValues) do
    local ok, validationMessage = validate_series(xValues, yValues[i])
    if not ok then
      log("G: invalid data -> returning error html")
      return validationMessage
    end
  end
  
  local configTable = build_chart_config(xValues, yValues, chartType,serieLabels,options)
  local configJson = js.window.encodeURIComponent(js.stringify(js.tojs(configTable)))
  log(configJson)
  local width = w 
  local height = h 
  local baseUrl = quickchart.baseUrl
  local version = quickchart.version

  local quickchartUrl =
    baseUrl .. '/chart?w=' .. width .. '&h=' .. height .. '&v=' .. version .. '&c=' .. configJson
    
  log(quickchartUrl)

  local html =
    '<div class="sb-chartjs-container">' ..
      '<img src="' .. quickchartUrl .. '" alt="Chart" />' ..
    '</div>'

  log("getHtml: end")
  return html
end

-- =========================
-- Commands 
-- =========================
function mls.table.insertLineBelow()  
  local function countPipesInCurrentLine()  
      local lineInfo = editor.getCurrentLine()  
      local lineText = lineInfo.text  
      local count = 0  
        
      -- Count all occurrences of "|" in the line  
      for _ in lineText:gmatch("|") do  
        count = count + 1  
      end  
        
      return count  
  end
  
  local pipeCount = countPipesInCurrentLine()  
  local cursor = editor.getCursor()  
  local coordonates=mls.positionToLineColumn(editor.getText(),cursor)
  local text = editor.getText()  
    
  -- Find current line number from cursor position  
  local lines = text:split("\n")  
  table.insert(lines, coordonates.line + 1,string.rep("|    ", pipeCount) )    
  editor.setText(table.concat(lines, "\n"))  
end

command.define {  
  name = "Table: Insert line below",  
  key = "Alt--",  
  run = function()  
    mls.table.insertLineBelow()
  end  
}

function mls.table.insertColumn()  
  local function insertDoublePipeAtPosition(lineText, position,fill)  
    local ch=string.split(lineText,"")
    table.insert(ch,position,"|"..fill)
    return table.concat(ch,"")
  end  

  local function  getListOfPipe(lineText)
    local posPipes = {}  
    for i = 1, string.len(lineText) do  
      if string.sub(lineText, i, i) == "|" then  
        table.insert(posPipes, i)  
      end  
    end  
    return posPipes
  end
  
  local text=editor.getText()
  local lines=  string.split(text,"\n")
  local cursorPos = editor.getCursor()  
  local coordonates=mls.positionToLineColumn(text,cursorPos)
  local lineText = lines[coordonates.line]

  local posPipes=getListOfPipe(lineText)

  -- Find nearest pipe to cursor position  
  local nearestPipe = 1  
  local minDistance = math.abs(coordonates.column - posPipes[1])  
    
  for i, pipePos in ipairs(posPipes) do  
    local distance = math.abs(coordonates.column - pipePos)  
    if distance < minDistance then  
      minDistance = distance  
      nearestPipe = i  
    end  
  end  
  -- Get all lines and find current line number  
  local currentLineNum =coordonates.line  

  local result={}
  local process=true
  -- Process lines below current line  
  for i = 1, #lines do  
    local line =lines[i]
    if  i>=currentLineNum and string.startsWith(line,"|") and process==true then  
      -- Insert double pipe at target position  
      local posL=getListOfPipe(line)[nearestPipe] 
      local fill="        "
      if i==currentLineNum + 1 then
        fill="--------"
      end  
      result[i] = insertDoublePipeAtPosition(line,posL, fill)  
    else
     result[i]=line
     if  i>currentLineNum then
       process=false
     end 
    end  
  end  
  -- Update the document  
  editor.setText(table.concat(result, "\n"))  
end

command.define {  
  name = "Table: Insert column",  
  key = "Alt-+",  
  run = function()  
   mls.table.insertColumn()
  end  
}  

local function extractTagsAndTitle(str)
    str = str or ""
    local tags = {}
    local words = {}
    local tab=string.split(str, " ")
    for _,w in ipairs(tab) do
        local word=string.trim(w)
        if word:sub(1,1) == "#" and #word > 1 then
            -- remove leading # using gsub
            local tag = string.gsub(word, "^#", "")
            table.insert(tags, tag)
        else
            table.insert(words, word)
        end
    end
    local title = table.concat(words, " ")
    return { tags = tags, title = title }
end

local function getTableColumnHeader()
  local text = editor.getText()
  local lines = string.split(text, "\n")
  local cursorPos = editor.getCursor()
  local coordonates = mls.positionToLineColumn(text, cursorPos)
  local lineIndex = coordonates.line
  local charColumn = coordonates.column
  local currentLine = lines[lineIndex]

  -- 1. Character column -> table column
  local tableColumn = 0
  for i = 1, charColumn do
    if string.sub(currentLine, i, i) == "|" then
      tableColumn = tableColumn + 1
    end
  end
  tableColumn = math.max(tableColumn, 1)

  -- 2. Find header line
  local headerLineIndex = nil
  for i = lineIndex - 1, 1, -1 do
    local line = string.trim(lines[i])
    local nextLine = string.trim(lines[i + 1] or "")
    local startT,endT=string.find(nextLine, "-%-%-")
    if string.startsWith(line, "|")
       and string.startsWith(nextLine, "|")
       and startT ~= nil and endT ~= nil  then
      headerLineIndex = i
      break
    end
  end
  if not headerLineIndex then
    return nil
  end

  -- 3. Extract header cells
  local headerLine = lines[headerLineIndex]
  local rawCells = string.split(headerLine, "|")
  return rawCells[tableColumn+1]
end

function mls.table.insertValue()
  local header=getTableColumnHeader()  
  local data=extractTagsAndTitle(header)

  if #data.tags>0 and mls.table.render then 
    local result=mls.table.render(data.title, data.tags)
    if result ~= nil then
     editor.insertAtCursor(result)
     return 
    end
  end
  editor.flashNotification("No renderer defined","error")
end

command.define {  
  name = "Table: Insert  value",  
  key = "Alt-/",  
  run = function()  
    mls.table.insertValue()
  end  
}

-- =========================
-- Main functions 
-- =========================

---
-- Main HTML widget function:
-- @param label string
-- @param pageName string
-- @param XRange string
-- @param YRange string
-- @param options table
-- @return string
---
function G(label, pageName, XRange, YRange, options)
  log("G: start")
  local YRanges=YRange
  if type(YRange) == "string" then
    YRanges={YRange}
  end  
 
  if not pageName or pageName == "" then
    pageName = editor.getCurrentPage()
  end

  local tables = extractTables(pageName)
  if not tables then
    return "No tables found on page"
  end
  local tbl = nil

  if label and label ~= "" then
    log("G: found table 1")
    tbl = tables[label]
  end

  if not tbl then
   tbl = getClosestTable(label,pageName,tables)
  end

  if not tbl then
   return "Missing table"
  end

  local cellMap = toCellMap(tbl)
  local xValues = XRange
  if type(XRange) == "string" then
    xValues = expandSingleRange(XRange, cellMap)
  end
  local yValues = table.map(YRanges, function(x)
    return expandSingleRange(x, cellMap)
  end) 

  local chartType="line"
  local w=400
  local h=600
  local serieLabels={}
  for i = 1, #yValues do
    table.insert(serieLabels, "Series "..tostring(i))
  end
  
  local chartOptions
  if type(options) == "table" then
    chartType = options.chartType or options.type or chartType
    w = options.w or options.width or w
    h = options.h or options.height or h
    if options.serieLabel then
      if type(options.serieLabel) == "table"then
        serieLabels=options.serieLabel
      else
        local seriesL=expandSingleRange(options.serieLabel, cellMap)
        if #seriesL >0  then
          serieLabels=seriesL
        end
      end
    end
    chartOptions = options.options
  end

  local html = getHtml(xValues, yValues, chartType,serieLabels, w, h,chartOptions)
  return widget.htmlBlock(html)
end
```


## Changelog

* 2026-02-08:
  * feat: support of multiple series
  * feat: support chartjs options
* 2026-02-01:
  * feat: command (alt+/) to insert formated data
*  2026-01-02 fix: call functions with many arguments 

## Community

[Silverbullet forum](https://community.silverbullet.md/t/feature-markdown-table-formula-with-formulajs/3208)
---
author: malys
description: Advanced spreadsheet extras for Markdown tables (pivot, formula palette, conditional formatting, CSV import). Companion to MdTableSheet / MdTableRender.
tags: userscript
pageDecoration.prefix: "🛎️"
name: "Library/Malys/MdTableSheetExtras"
---
# Md Table Sheet — Extras

Companion add-ons to [[Library/Malys/MdTableSheet]] (formula/chart engine) and
[[Library/Malys/MdTableRender]] (column renderers). These features live in their
own file so the frozen MdTableSheet plugin is left untouched; they reuse the
`mls.table` namespace and the same conventions.

## Features

1. **Pivot tables** — `${P(label, groupCol, valueCol, agg)}` aggregates a table
   (group by one column, aggregate another with `sum`/`avg`/`count`/`min`/`max`)
   and renders the result as an inline HTML table.
2. **Formula palette** — command **Table: Insert formula** (and slash `/formula`)
   opens a filter box of common Formulajs functions and inserts a ready-to-edit
   `${F("…")}` snippet with the cursor placed inside.
3. **Conditional formatting** — column header tags `#heat`, `#heatr`, `#databar`
   color cells relative to the min/max of their column (heatmap / reversed
   heatmap / proportional data bar). Implemented as a self-contained injected
   runtime (the MdTableRender engine is cell-by-cell and cannot see a whole
   column).
4. **CSV/TSV import** — command **Table: Import CSV/TSV** (and slash `/csvtable`)
   turns clipboard (or prompted) delimited text into a Markdown table at the
   cursor. Auto-detects `,` / `;` / tab.

---

## Pivot

`P(label, groupCol, valueCol, agg, options)`

- `label` (string): unique id used to locate the pivot's source table — the
  table **closest above** the `${P("label", …)}` call, same logic as `G`.
- `groupCol` (string): column letter to group by (e.g. `"A"`).
- `valueCol` (string): column letter holding the numbers to aggregate (e.g. `"C"`).
- `agg` (string, optional): `sum` (default), `avg`, `count`, `min`, `max`.
- `options` (table, optional): `{ title = "…" }` header label for the value column.

| Category | Item | Amount |
| --- | --- | --- |
| Food | Apple | 3 |
| Food | Bread | 5 |
| Tech | Mouse | 20 |
| Tech | Cable | 8 |
| Food | Milk | 2 |

${P("demo", "A", "C", "sum")}

## Formula palette

Run **Table: Insert formula** or type `/formula`, pick a function, and a
`${F("…")}` snippet is inserted with the cursor inside the argument list.

## Conditional formatting

Add a tag to the column header (the tag is hidden on render):

```md
| Day | Energy #heat | Pain #heatr | Steps #databar |
| --- | ------------ | ----------- | -------------- |
| Mon | 2            | 4           | 3000           |
| Tue | 8            | 1           | 9000           |
| Wed | 5            | 3           | 6000           |
```

- `#heat` — low = green, high = red (e.g. cost, errors).
- `#heatr` — reversed: low = red, high = green (e.g. energy, score).
- `#databar` — proportional bar in the cell background.

Commands: **Table: Enable Conditional Formatting** / **Table: Disable
Conditional Formatting**. Auto-starts unless disabled via the
`tableConditionalFormat` config (`{ enabled = false }`).

## CSV/TSV import

Run **Table: Import CSV/TSV** (reads the clipboard) or `/csvtable`. The delimiter
is auto-detected from the first line; pipes inside values are escaped.

## Code source

```space-lua
-- luacheck: globals P
-- ---------------------------
-- Md Table Sheet — Extras
-- Companion to MdTableSheet (F/G/R) and MdTableRender (mls.table.renderer).
-- Reuses the mls.table namespace. Standalone: re-derives table extraction from
-- the index because MdTableSheet's helpers are file-local.
-- ---------------------------
mls = mls or {}
mls.table = mls.table or {}
mls.table.extras = mls.table.extras or {}

local function log(...)
  if LOG_ENABLE and mls and mls.debug then
    if type(mls.debug) == "function" then
      mls.debug({ ... })
    end
  end
end

-- Index metadata keys that are NOT table cell values (mirrors MdTableSheet.META).
local META = {
  ref = true, tag = true, tags = true, itags = true,
  page = true, pos = true, tableref = true, range = true,
}

-- =========================
-- Shared table extraction (column letters <-> numbers, cell maps)
-- =========================

local function colToNumber(col)
  local n = 0
  for i = 1, string.len(col) do
    n = n * 26 + (string.byte(col, i) - string.byte("A") + 1)
  end
  return n
end

-- Convert one index row into an ordered array of cell values (skips META keys).
-- Relies on insertion-ordered keys, exactly like MdTableSheet.extractTable.
local function extractRow(row)
  local rowData = {}
  local col = 1
  for k, v in pairs(row) do
    if not META[k] then
      rowData[col] = v
      col = col + 1
    end
  end
  return rowData
end

-- Returns a map of tableref -> array-of-rows(array-of-cells) for a page.
local function extractTables(pageName)
  if not pageName or pageName == "" then pageName = editor.getCurrentPage() end
  local allRows = query[[from index.tag "table" where page == pageName order by pos]]
  local groups = {}
  for _, row in ipairs(allRows) do
    local ref = row.tableref
    if not groups[ref] then groups[ref] = {} end
    table.insert(groups[ref], extractRow(row))
  end
  return groups
end

-- Position of a literal pattern in a page (used to locate the closest table).
local function findPosition(pageName, pattern)
  if not pageName or pageName == "" then pageName = editor.getCurrentPage() end
  local page = space.readPage(pageName)
  if not page then return nil end
  local s = string.find(page, pattern, 1, true)
  return s
end

-- Returns the table (array of rows) nearest *above* the call site, matching
-- MdTableSheet's getClosestTable strategy (tableref carries a @position).
local function getClosestTable(callPattern, pageName, tables)
  local callPos = tonumber(findPosition(pageName, callPattern)) or 0
  local minDiff = 1e9
  local nearest
  for _, t in pairs(tables) do nearest = t; break end -- fallback: any table
  for ref, t in pairs(tables) do
    local tablePos = tonumber(string.match(ref, "@([0-9]+)")) or 0
    local diff = callPos - tablePos
    if diff >= 0 and diff < minDiff then
      minDiff = diff
      nearest = t
    end
  end
  return nearest
end

-- =========================
-- 1) Pivot: P(label, groupCol, valueCol, agg, options)
-- =========================

local function aggregate(values, agg)
  local n = #values
  if agg == "count" then return n end
  if n == 0 then return 0 end
  if agg == "min" then
    local m = values[1]
    for _, v in ipairs(values) do if v < m then m = v end end
    return m
  end
  if agg == "max" then
    local m = values[1]
    for _, v in ipairs(values) do if v > m then m = v end end
    return m
  end
  local sum = 0
  for _, v in ipairs(values) do sum = sum + v end
  if agg == "avg" then return sum / n end
  return sum -- default: sum
end

local function formatNumber(v)
  if type(v) ~= "number" then return tostring(v) end
  if v == math.floor(v) then return string.format("%d", v) end
  return string.format("%.2f", v)
end

function P(label, groupCol, valueCol, agg, options)
  log("P: start " .. tostring(label))
  agg = agg or "sum"
  options = options or {}

  local pageName = editor.getCurrentPage()
  local tables = extractTables(pageName)
  if not next(tables) then return "No tables found on page" end

  local tbl = getClosestTable('P("' .. tostring(label) .. '"', pageName, tables)
  if not tbl then return "Pivot: source table not found" end

  local gIdx = colToNumber(string.upper(groupCol))
  local vIdx = colToNumber(string.upper(valueCol))

  -- Group preserving first-seen order.
  local order = {}
  local buckets = {}
  for _, row in ipairs(tbl) do
    local key = tostring(row[gIdx] or "")
    local num = tonumber(row[vIdx])
    if not buckets[key] then
      buckets[key] = {}
      table.insert(order, key)
    end
    if num ~= nil then table.insert(buckets[key], num) end
  end

  local valueTitle = options.title or (string.upper(agg) .. " " .. string.upper(valueCol))
  local html = '<div class="sb-pivot-container"><table class="sb-pivot"><thead><tr>' ..
    '<th>' .. string.upper(groupCol) .. '</th><th>' .. valueTitle .. '</th></tr></thead><tbody>'
  for _, key in ipairs(order) do
    local result = aggregate(buckets[key], agg)
    html = html .. '<tr><td>' .. key .. '</td><td style="text-align:right">' ..
      formatNumber(result) .. '</td></tr>'
  end
  html = html .. '</tbody></table></div>'

  log("P: end")
  return widget.htmlBlock(html)
end

-- =========================
-- 2) Formula palette
-- =========================

-- Curated Formulajs functions. value uses the |^| caret marker so the cursor
-- lands inside the argument list after insertion.
local formulaPalette = {
  { name = "SUM — sum of a range",            value = [[${F("SUM(|^|A1:A5)")}]] },
  { name = "AVERAGE — mean of a range",       value = [[${F("AVERAGE(|^|A1:A5)")}]] },
  { name = "COUNT — count numeric cells",     value = [[${F("COUNT(|^|A1:A5)")}]] },
  { name = "MIN — smallest value",            value = [[${F("MIN(|^|A1:A5)")}]] },
  { name = "MAX — largest value",             value = [[${F("MAX(|^|A1:A5)")}]] },
  { name = "MEDIAN — median of a range",      value = [[${F("MEDIAN(|^|A1:A5)")}]] },
  { name = "PRODUCT — multiply a range",      value = [[${F("PRODUCT(|^|A1:A5)")}]] },
  { name = "SUMIF — conditional sum",         value = [[${F("SUMIF(|^|A1:A5,\">0\")")}]] },
  { name = "COUNTIF — conditional count",     value = [[${F("COUNTIF(|^|A1:A5,\">0\")")}]] },
  { name = "ROUND — round a cell",            value = [[${F("ROUND(|^|A1,2)")}]] },
  { name = "ABS — absolute value",            value = [[${F("ABS(|^|A1)")}]] },
  { name = "CONCAT — join two cells",         value = [[${F("CONCAT(|^|A1,B1)")}]] },
  { name = "IF — conditional value",          value = [[${F("IF(|^|A1>0,\"yes\",\"no\")")}]] },
  { name = "STDEV — standard deviation",      value = [[${F("STDEV(|^|A1:A5)")}]] },
  { name = "Raw cell reference (A1)",         value = [[${F("|^|A1")}]] },
}

function mls.table.insertFormula()
  local choice = editor.filterBox("Formula", formulaPalette)
  if not choice then return end
  local snippet = choice
  if type(choice) == "table" and choice.value then snippet = choice.value end
  editor.insertAtCursor(snippet, false, true)
end

command.define {
  name = "Table: Insert formula",
  run = function() mls.table.insertFormula() end
}

slashcommand.define {
  name = "formula",
  description = "Insert a Formulajs table formula",
  run = function() mls.table.insertFormula() end
}

-- =========================
-- 4) CSV/TSV import  (defined before the injected CF runtime for readability)
-- =========================

local function detectDelimiter(firstLine)
  -- Tab / ; / , are not Lua pattern magic chars, so each can be matched literally.
  local best, bestCount = ",", 0
  for _, d in ipairs({ "\t", ";", "," }) do
    local count = 0
    for _ in string.gmatch(firstLine, d) do count = count + 1 end
    if count > bestCount then best, bestCount = d, count end
  end
  return best
end

local function csvToMarkdown(text, delimiter)
  text = string.gsub(text, "\r\n", "\n")
  text = string.gsub(text, "\r", "\n")
  local lines = {}
  for _, l in ipairs(string.split(text, "\n")) do
    if string.trim(l) ~= "" then table.insert(lines, l) end
  end
  if #lines == 0 then return nil end

  local delim = delimiter or detectDelimiter(lines[1])

  local function cells(line)
    local out = {}
    for _, c in ipairs(string.split(line, delim)) do
      local cell = string.trim(c)
      cell = string.gsub(cell, "|", "\\|") -- escape pipes
      table.insert(out, cell)
    end
    return out
  end

  local header = cells(lines[1])
  local md = { "| " .. table.concat(header, " | ") .. " |" }
  local sep = {}
  for _ = 1, #header do table.insert(sep, "---") end
  table.insert(md, "| " .. table.concat(sep, " | ") .. " |")
  for i = 2, #lines do
    table.insert(md, "| " .. table.concat(cells(lines[i]), " | ") .. " |")
  end
  return table.concat(md, "\n") .. "\n"
end

function mls.table.importCsv()
  local text
  local ok, clip = pcall(function()
    return js.window.navigator.clipboard.readText()
  end)
  if ok and type(clip) == "string" and string.trim(clip) ~= "" then
    text = clip
  else
    text = editor.prompt("Paste CSV/TSV (one row, or whole block if supported)")
  end
  if not text or string.trim(text) == "" then
    editor.flashNotification("Nothing to import", "error")
    return
  end
  local md = csvToMarkdown(text)
  if not md then
    editor.flashNotification("Could not parse CSV/TSV", "error")
    return
  end
  editor.insertAtCursor(md)
end

command.define {
  name = "Table: Import CSV/TSV",
  run = function() mls.table.importCsv() end
}

slashcommand.define {
  name = "csvtable",
  description = "Import clipboard CSV/TSV as a Markdown table",
  run = function() mls.table.importCsv() end
}

-- =========================
-- 3) Conditional formatting (self-contained injected runtime)
-- =========================
-- Cell-by-cell renderers (MdTableRender) cannot see a whole column, and that
-- file reassigns mls.table.renderer wholesale, so heat/databar would be lost.
-- This is therefore an independent runtime mirroring enableTableRenderer.

config.define("tableConditionalFormat", { type = "object" })

local cfId = "sb-table-cf-runtime"

function mls.table.disableConditionalFormat()
  local existing = js.window.document.getElementById(cfId)
  if existing then
    local ev = js.window.document.createEvent("Event")
    ev.initEvent("sb-table-cf-unload", true, true)
    js.window.dispatchEvent(ev)
    existing.remove()
    print("Table CF: Disabled")
  else
    print("Table CF: Already inactive")
  end
end

function mls.table.enableConditionalFormat()
  if js.window.document.getElementById(cfId) then
    print("Table CF: Already active")
    return
  end
  local scriptEl = js.window.document.createElement("script")
  scriptEl.id = cfId
  scriptEl.innerHTML = [[
(function () {
  'use strict';
  const MODES = { heat: 1, heatr: 1, databar: 1 };

  function columnModes(table) {
    const headerRow = table.querySelector('thead tr') || table.querySelector('tr');
    if (!headerRow) return null;
    const cells = headerRow.cells;
    const modes = [];
    let any = false;
    for (let i = 0; i < cells.length; i++) {
      modes[i] = null;
      const tags = cells[i].querySelectorAll('a.hashtag,[data-tag-name]');
      for (let t = 0; t < tags.length; t++) {
        const el = tags[t];
        const name = (el.dataset && el.dataset.tagName) ? el.dataset.tagName : el.textContent.replace('#', '');
        const base = name.replace(/\d+$/, '');
        if (MODES[base]) { modes[i] = base; el.style.display = 'none'; any = true; break; }
      }
    }
    return any ? modes : null;
  }

  function processTable(table) {
    if (table.dataset.sbCf) return;
    const modes = columnModes(table);
    const tbody = table.tBodies[0];
    if (!modes || !tbody) { table.dataset.sbCf = 'true'; return; }
    const rows = tbody.rows;

    // per-column min/max over numeric cells
    const stats = {};
    for (let c = 0; c < modes.length; c++) {
      if (!modes[c]) continue;
      let mn = Infinity, mx = -Infinity;
      for (let r = 0; r < rows.length; r++) {
        const cell = rows[r].cells[c];
        if (!cell) continue;
        const num = parseFloat(cell.textContent.trim().replace(',', '.'));
        if (!isNaN(num)) { if (num < mn) mn = num; if (num > mx) mx = num; }
      }
      stats[c] = { mn, mx };
    }

    for (let r = 0; r < rows.length; r++) {
      for (let c = 0; c < modes.length; c++) {
        const mode = modes[c];
        if (!mode) continue;
        const cell = rows[r].cells[c];
        if (!cell) continue;
        const num = parseFloat(cell.textContent.trim().replace(',', '.'));
        if (isNaN(num)) continue;
        const s = stats[c];
        const range = (s.mx - s.mn) || 1;
        const t = (num - s.mn) / range; // 0..1
        if (mode === 'heat' || mode === 'heatr') {
          const tt = mode === 'heatr' ? (1 - t) : t;
          const hue = 120 * (1 - tt); // 120=green .. 0=red
          cell.style.background = 'hsl(' + hue + ',70%,85%)';
        } else if (mode === 'databar') {
          const pct = Math.round(t * 100);
          cell.style.background = 'linear-gradient(90deg, var(--cf-bar,#9ecbff) ' + pct + '%, transparent ' + pct + '%)';
        }
        cell.dataset.sbCfCell = '1';
      }
    }
    table.dataset.sbCf = 'true';
  }

  function scan() {
    const tables = document.querySelectorAll('#sb-editor table:not([data-sb-cf])');
    for (let i = 0; i < tables.length; i++) processTable(tables[i]);
  }

  let to;
  const observer = new MutationObserver(() => {
    if (to) clearTimeout(to);
    to = setTimeout(scan, 60);
  });
  observer.observe(document.body, { childList: true, subtree: true });
  scan();

  window.addEventListener('sb-table-cf-unload', function cln() {
    observer.disconnect();
    const cells = document.querySelectorAll('[data-sb-cf-cell]');
    for (let i = 0; i < cells.length; i++) {
      cells[i].style.background = '';
      cells[i].removeAttribute('data-sb-cf-cell');
    }
    const tables = document.querySelectorAll('table[data-sb-cf]');
    for (let i = 0; i < tables.length; i++) delete tables[i].dataset.sbCf;
    window.removeEventListener('sb-table-cf-unload', cln);
  });
})();
  ]]
  js.window.document.body.appendChild(scriptEl)
end

command.define {
  name = "Table: Enable Conditional Formatting",
  run = function() mls.table.enableConditionalFormat() end
}

command.define {
  name = "Table: Disable Conditional Formatting",
  run = function() mls.table.disableConditionalFormat() end
}

-- Autostart
local cfCfg = config.get("tableConditionalFormat") or {}
if cfCfg.enabled ~= false then
  mls.table.enableConditionalFormat()
else
  mls.table.disableConditionalFormat()
end
```

## Changelog

* 2026-05-29:
  * feat: pivot tables `${P(label, groupCol, valueCol, agg)}` (sum/avg/count/min/max)
  * feat: formula palette — command **Table: Insert formula** + slash `/formula`
  * feat: conditional formatting column tags `#heat` / `#heatr` / `#databar` via an independent injected runtime
  * feat: CSV/TSV import — command **Table: Import CSV/TSV** + slash `/csvtable` (clipboard, delimiter auto-detect)

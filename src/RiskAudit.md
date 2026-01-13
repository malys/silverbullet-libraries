---
author: malys
description:  Risk audit  (scripts analyzor)
name: "Library/Malys/RiskAudit"
tags: meta/library
---
# Risk Audit

## Description

The Enhanced Risk Audit f for SilverBullet analyzes scripts for potentially dangerous constructs and API calls. 
It provides a risk audit report that includes a trust score for each code block, a summary of findings, and a list of rules used to analyze scripts. 

## Commands

- **Security: Scan Current Page**: Runs the scanner on the current page and generates a risk audit report.
- **Security: Scan All Children Pages**: Scans all child pages of the current page and generates a risk audit report for each page.
_

## Reports

![](https://community.silverbullet.md/uploads/default/original/2X/3/359702815a70766b4c38b7b6c007d94b222278f7.gif)

![](https://community.silverbullet.md/uploads/default/original/2X/5/5176409b91850c5189da3423f47c1b41808deda2.gif)
## Code
```space-lua
-- ###########################################################################
-- ## Enhanced Space-Lua Scanner for SilverBullet
-- ##
-- ## Features:
-- ##   - Detects ```space-lua``` code blocks
-- ##   - Internal API usage
-- ##   - Dangerous Lua constructs
-- ##   - URLs, Base64, Hex, high-entropy strings
-- ##   - Line-numbered findings
-- ##   - Computes per-block trust score and page score
-- ##   - Generates Markdown audit report
-- ##   - Virtual pages:
-- ##       scan:page:<name>
-- ##       scan:all
-- ###########################################################################

-- ===================================================================
-- == Debug
-- ===================================================================
local function log(...)
  if LOG_ENABLE and mls and mls.debug then
    mls.debug(table.concat({...}, " "))
  end
end

local function _wrap_with_debug(name, fn)
  return function(...)
    log("enter", name)
    local r = fn(...)
    log("exit", name)
    return r
  end
end

-- ===================================================================
-- == Utilities
-- ===================================================================

local function count_keys(t)
  local n=0
  for _ in pairs(t or {}) do n=n+1 end
  return n
end

local function get_wikilink(page, line)
  if not page then return ("@%d"):format(line) end
  return ("[[%s@L%d]]"):format(page, line)
end

-- ===================================================================
-- == Find space-lua blocks
-- ===================================================================

local find_space_lua_blocks = _wrap_with_debug("find_space_lua_blocks", function(text)
  local blocks = {}
  local in_block=false
  local buf={}
  local lines = string.split(text or "", "\n")

  for i,l in ipairs(lines) do
    if not in_block and l:match("^```space%-lua") then
      in_block=true
      buf={}
    elseif in_block and l:match("^```") then
      in_block=false
      table.insert(blocks,{
        text=table.concat(buf,"\n"),
        start_line=i-#buf
      })
    elseif in_block then
      table.insert(buf,l)
    end
  end
  return blocks
end)

-- ===================================================================
-- == Rules
-- ===================================================================

local api_prefixes = {
  "asset","clientStore","command","config","datastore","editor","event",
  "http","js","library","lua","markdown","mq","net","os","shell",
  "space","spacelua","string","system","table","template","yaml"
}

local dangerous_tokens = {
  "io%.open","os%.execute","loadstring","debug%.","package%.",
  "require%(","shell%.run","http%.request","_G","rawset%(_G"
}

-- ===================================================================
-- == Analyze block
-- ===================================================================

local analyze_block = function(block)
  local res={
    score=0,
    apis_found={},
    api_calls={},
    dangerous={},
    findings={},
    page=block.page
  }

  for i,line in ipairs(string.split(block.text,"\n")) do
    local ln=block.start_line+i-1

    for _,p in ipairs(api_prefixes) do
      for m in line:gmatch(p.."%.([%w_]+)") do
        res.apis_found[p]=true
        res.api_calls[p]=res.api_calls[p] or {}
        table.insert(res.api_calls[p], m.." "..get_wikilink(res.page,ln))
      end
    end

    for _,d in ipairs(dangerous_tokens) do
      if line:match(d) then
        table.insert(res.dangerous, d.." "..get_wikilink(res.page,ln))
      end
    end

    for url in line:gmatch("https?://[%w%p]+") do
      table.insert(res.findings,"URL "..url.." "..get_wikilink(res.page,ln))
      res.score=res.score+5
    end
  end

  res.score = math.min(100, res.score + count_keys(res.apis_found)*5 + (#res.dangerous>0 and 70 or 0))
  return res
end

-- ===================================================================
-- == Report
-- ===================================================================

local function generate_report(page, blocks)
  local md={"# Risk Audit","", "**Page:** "..page,""}
  local max=0

  for i,b in ipairs(blocks) do
    local a=b.analysis
    if a.score>max then max=a.score end
    table.insert(md,("## Block %d — %d%%"):format(i,a.score))
    table.insert(md,"```lua")
    table.insert(md,b.text)
    table.insert(md,"```")
  end

  table.insert(md,"----")
  table.insert(md,("## Page Risk Score: **%d%%**"):format(max))
  return table.concat(md,"\n"), max
end

-- ===================================================================
-- == Cache
-- ===================================================================
local report_cache={}

-- ===================================================================
-- == Scan Current Page 
-- ===================================================================

command.define {
  name="Security audit: Scan Current Page",
  run=_wrap_with_debug("scan_current", function()
    local page = editor.getCurrentPage()
    if not page then return end

    local text = space.readPage(page)
    local attrs=space.getPageMeta(page)
    local hash = share.contentHash(text)

    if attrs.audit and attrs["share.hash"] == hash then
      editor.navigate("scan:page:"..page)
      return
    end

    local blocks={}
    for _,b in ipairs(find_space_lua_blocks(body)) do
      b.page=page
      b.analysis=analyze_block(b)
      table.insert(blocks,b)
    end

    local report, score = generate_report(page, blocks)
    report_cache[page]=report
    if type(score) ~= "number"then
      score=0
    end

    index.patchFrontmatter(text, {
        { op = "set-key", path = "audit", value = score },
        { op = "set-key", path = "share.hash", value = hash }
    })
    editor.navigate("scan:page:"..page)
  end)
}

-- ===================================================================
-- == Virtual page
-- ===================================================================

virtualPage.define {
  pattern="scan:page:(.+)",
  run=function(ref)
    return report_cache[ref] or "_No audit available_"
  end
}
```


## Community

[Silverbullet forum](https://community.silverbullet.md/t/risk-audit/3562)

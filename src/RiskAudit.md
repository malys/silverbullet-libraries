---
author: malys
description:  Risk audit  (scripts analyzor)
pageDecoration.prefix: "👮 "
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

-- ===========================================================================
-- == Debug wrapper
-- ===========================================================================
local cond3 = (mls ~= nil and mls.cache ~= nil and mls.cache.ttl == nil)
if library ~= nil and (mls == nil or (mls ~= nil and mls.debug == nil) or (mls ~= nil and mls.cache == nil) or cond3) then
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Debugger.md")
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/cache/TTL.md")
	editor.flashNotification("'Depencies' has been installed", "Info")
end

local function log(...)
	if LOG_ENABLE and mls and mls.debug then
		if type(mls.debug) == "function" then
			mls.debug(table.concat({
				...
			}, " "))
		end
	end
end

local function _wrap_with_debug(name, fn)
	return function(...)
		log("enter " .. name)
		local res = fn(...)
		log("exit " .. name)
		return res
	end
end

-- ===========================================================================
-- == Utilities
-- ===========================================================================
local trim = _wrap_with_debug("trim", function(s)
	return string.trim(s or "")
end)

local tconcat = _wrap_with_debug("tconcat", function(tbl, sep)
	sep = sep or "\n"
	return table.concat(tbl or {}, sep)
end)

local function count_keys(tbl)
	local n = 0
	for _ in pairs(tbl) do
		n = n + 1
	end
	return n
end

local function get_wikilink(page, line)
	if not page then
		return ("@%d"):format(line)
	end
	return ("[[%s@L%d]]"):format(page, line)
end

-- ===========================================================================
-- == Scanner: find code blocks
-- ===========================================================================
local find_space_lua_blocks = _wrap_with_debug("find_space_lua_blocks", function(text)
	local blocks = {}
	if not text or text == "" then
		return blocks
	end
	local in_block = false
	local current = {}
	local lines = string.split(text, "\n")
	for i, line in ipairs(lines) do
		if not in_block and string.startsWith(line, "```space-lua") then
			in_block = true
			current = {}
		elseif in_block and string.startsWith(line, "```") then
			in_block = false
			table.insert(blocks, {
				text = string.trim(table.concat(current, "\n")),
				start_line = i - # current
			})
		elseif in_block then
			table.insert(current, line)
		end
	end
	return blocks
end)

-- ===========================================================================
-- == Rules (modular, maintainable)
-- ===========================================================================
local default_prefixes = {
	"asset",
	"clientStore",
	"codeWidget",
	"command",
	"config",
	"datastore",
	"editor",
	"encoding",
	"event",
	"global",
	"http",
	"index",
	"js",
	"jsonschema",
	"language",
	"library",
	"lua",
	"markdown",
	"math",
	"mq",
	"net",
	"os",
	"service",
	"shell",
	"slashCommand",
	"space",
	"spacelua",
	"string",
	"sync",
	"system",
	"table",
	"template",
	"yaml"
}
local remote_prefixes = mls.getStdlibInternal()

local api_prefixes = table.unique(table.appendArray(default_prefixes, remote_prefixes))

local dangerous_tokens = {-- File I/O and OS operations
	"io%.open",
	"os%.execute",
	"os%.remove",
	"os%.rename",
	"os%.exit",-- Dynamic code execution
	"loadstring",
	"load%(",
	"dofile%(",-- Debug and introspection
	"getmetatable",
	"setmetatable",
	"rawset",
	"rawget",-- Global environment access
	"_G",
	"rawset%(_G",
	"rawget%(_G",
	"_CTX",-- Module and library loading
	"package%.",
	"require%(",
	"library%.",-- JavaScript interop (SilverBullet specific)
	"js%.",-- Network operations
	"http%.request%(",
	"net%.",-- Shell execution (SilverBullet specific)
	"shell%.run%(",-- SilverBullet specific APIs
	"crypto%.",-- Cryptographic operations
	"encoding%.",   -- Encoding/decoding  
}

-- ===========================================================================
-- == Analysis: per-block
-- ===========================================================================
local analyze_block = _wrap_with_debug("analyze_block", function(block)
	local block_text = block.text or ""
	local start_line = block.start_line or 1
	local analysis = {
		summary = "",
		findings = {},
		apis_found = {},
		api_calls = {},
		dangerous = {},
		score = 0,
		page = block.page
	}
	if block_text == "" then
		analysis.summary = "Empty code block"
		return analysis
	end
	local api_set = {}
	for _, p in ipairs(api_prefixes) do
		api_set[p] = true
	end
	for line_num, line in ipairs(string.split(block_text, "\n")) do
		local ln = start_line + line_num - 1

    ----------------------------------------------------------------------
    -- Internal API
    ----------------------------------------------------------------------
		for prefix in pairs(api_set) do
			for method in string.gmatch(line, prefix .. "%.(%w+)") do
				analysis.apis_found[prefix] = true
				analysis.api_calls[prefix] = analysis.api_calls[prefix] or {}
				table.insert(
          analysis.api_calls[prefix], ("%s() %s"):format(method, get_wikilink(analysis.page, ln)))
			end
		end

    ----------------------------------------------------------------------
    -- Dangerous tokens
    ----------------------------------------------------------------------
		for _, tok in ipairs(dangerous_tokens) do
			if string.find(line, tok) then
				table.insert(
          analysis.dangerous, ("%s %s"):format(tok, get_wikilink(analysis.page, ln)))
			end
		end

    ----------------------------------------------------------------------
    -- URL detection
    ----------------------------------------------------------------------
		for url in string.gmatch(line, "https?://[%w%._/%-%?&=]+") do
			table.insert(
        analysis.findings, ("URL detected: %s %s"):format(url, get_wikilink(analysis.page, ln)))
			analysis.score = analysis.score + 5
		end

    ----------------------------------------------------------------------
    -- Base64 detection
    ----------------------------------------------------------------------
		for b64 in string.gmatch(line, "([A-Za-z0-9+/=]+)") do
			if # b64 >= 64 and # b64 % 4 == 0 then
				table.insert(
          analysis.findings, ("Base64 blob detected %s"):format(get_wikilink(analysis.page, ln)))
				analysis.score = analysis.score + 10
			end
		end

    ----------------------------------------------------------------------
    -- Hex blob
    ----------------------------------------------------------------------
		for hx in string.gmatch(line, "([A-Fa-f0-9]+)") do
			if # hx >= 32 and # hx % 2 == 0 then
				table.insert(
          analysis.findings, ("Hex blob detected %s"):format(get_wikilink(analysis.page, ln)))
				analysis.score = analysis.score + 10
			end
		end

    ----------------------------------------------------------------------
    -- High entropy
    ----------------------------------------------------------------------
		local count_print = 0
		for c in line:gmatch(".") do
			if c:match("%S") then
				count_print = count_print + 1
			end
		end
		if # line > 200 and count_print / # line > 0.8 then
			table.insert(
        analysis.findings, ("High-entropy string %s"):format(get_wikilink(analysis.page, ln)))
			analysis.score = analysis.score + 15
		end
	end

  ----------------------------------------------------------------------
  -- Scoring
  ----------------------------------------------------------------------
	local api_count = count_keys(analysis.apis_found)
	if api_count > 0 then
		analysis.score = analysis.score + (api_count * 5)
	end
	if # analysis.dangerous > 0 then
		analysis.score = analysis.score + 70
	end
	if analysis.score > 100 then
		analysis.score = 100
	end
	local severity = "Low"
	if analysis.score > 90 then
		severity = "Critical"
	elseif analysis.score > 70 then
		severity = "High"
	elseif analysis.score > 40 then
		severity = "Medium"
	end
	analysis.summary = string.format("Score=%d (%s) APIs=%d Dangerous=%d Findings=%d", analysis.score, severity, api_count, # analysis.dangerous, # analysis.findings)
	return analysis
end)

-- ===========================================================================
-- == Page scoring
-- ===========================================================================
local compute_page_score = _wrap_with_debug("compute_page_score", function(analyses)
	local result = 0
	for _, a in ipairs(analyses) do
		if a.score > result then
			result = a.score
		end
	end
	return math.floor(result)
end)


-- ===========================================================================
-- == Report generation
-- ===========================================================================
local generate_report = _wrap_with_debug("generate_report", function(page_name, blocks)
	local md = {}
	table.insert(md, "# Risk Audit")
	table.insert(md, "")
	table.insert(md, "**Page:** [[" .. (page_name or "(unknown)") .. "]]")
	table.insert(md, "")
	if not blocks or # blocks == 0 then
		table.insert(md, "_No space-lua code blocks found._")
		return table.concat(md, "\n")
	end
	local analyses = {}
	for i, blk in ipairs(blocks) do
		local A = blk.analysis
		table.insert(md, ("## Block %d — Score %d%%"):format(i, A.score))
		table.insert(md, "```lua")
		local shown = 0
		for line in string.gmatch(blk.text, "[^\r\n]+") do
			table.insert(md, line)
			shown = shown + 1
			if shown >= 12 then
				break
			end
		end
		if shown < #(string.split(blk.text, "\n")) then
			table.insert(md, "... (truncated)")
		end
		table.insert(md, "```")
		table.insert(md, "")
		table.insert(md, "**Summary:** " .. A.summary)
		table.insert(md, "")
		if next(A.api_calls) then
			table.insert(md, "**Internal API Calls:**")
			for api, calls in pairs(A.api_calls) do
				table.insert(md, ("- `%s`: %s"):format(api, table.concat(calls, ", ")))
			end
			table.insert(md, "")
		end
		if # A.dangerous > 0 then
			table.insert(md, "**Dangerous Constructs:**")
			for _, d in ipairs(A.dangerous) do
				table.insert(md, "- " .. d)
			end
			table.insert(md, "")
		end
		if # A.findings > 0 then
			table.insert(md, "**Suspicious Findings:**")
			for _, f in ipairs(A.findings) do
				table.insert(md, "- " .. f)
			end
			table.insert(md, "")
		end
		table.insert(analyses, A)
	end
	local page_score = compute_page_score(analyses)
	local severity = "Low"
	if page_score > 90 then
		severity = "Critical"
	elseif page_score > 70 then
		severity = "High"
	elseif page_score > 40 then
		severity = "Medium"
	end
	table.insert(md, "----")
	table.insert(md, ("## Page Risk Score: **%d%% (%s Risk)**"):format(page_score, severity))
	table.insert(md, "")
	table.insert(md, "_Legend:_")
	table.insert(md, "- Critical: 90–100%")
	table.insert(md, "- High: 70–89%")
	table.insert(md, "- Medium: 40–69%")
	table.insert(md, "- Low: 0–39%")
	table.insert(md, "")
	table.insert(md, "----")
	table.insert(md, "## Code quality: **1st space-lua code block**")
	table.insert(md, '${mls.debugger("check",{},"' .. page_name .. '")}')
	table.insert(md, "")
	table.insert(md, "----")
	table.insert(md, "_Audit generated by enhanced Malys Risk Audit_")
	return table.concat(md, "\n")
end)

local function generate_reports(page_name)
	local content = encoding.utf8Decode(space.readFile(page_name .. ".md"))
	local hash = share.contentHash(content)
	local report = mls.cache.ttl.CacheManager.get(hash)
	if report == nil then
		local raw_blocks = find_space_lua_blocks(content)
		local blocks = {}
		for _, b in ipairs(raw_blocks) do
			b.page = page_name
			local a = analyze_block(b, content)
			table.insert(blocks, {
				text = b.text,
				start_line = b.start_line,
				analysis = a
			})
		end
		report = generate_report(page_name, blocks)
		mls.cache.ttl.CacheManager.set(hash, report)
	end
	return report
end

-- ===========================================================================
-- == Virtual pages
-- ===========================================================================
virtualPage.define{
	pattern = "scan:page:(.+)",
	run = _wrap_with_debug("virtual_run_scan", function(ref)
		local page = ref or ""
		local rep = mls.cache.ttl.CacheManager.get(share.contentHash(space.readPage(page)))
		if not rep then
			return "Scan report not available for page: " .. page
		end
		return rep
	end)
}

-- ===========================================================================
-- == Virtual Page: Children Summary
-- ===========================================================================
virtualPage.define{
	pattern = "scan:(.+):children",
	run = _wrap_with_debug("virtual_run_children_summary", function(ref)
		local page_name = ref
		local summary = mls.cache.ttl.CacheManager.get("children_summary:" .. page_name) or {}
		local md = {
			"# Risk Scan: Children of " .. (page_name or ""),
			""
		}
		if # summary == 0 then
			table.insert(md, "_No child pages found or scanned._")
		else
      -- sort descending by score
			table.sort(summary, function(a, b)
				return tonumber(a.score) > tonumber(b.score)
			end)
			for _, s in ipairs(summary) do
				table.insert(md, string.format("- [%s](scan:page:%s) : %d%%", s.page, s.page, s.score))
			end
		end
		return table.concat(md, "\n")
	end)
}


-- ===========================================================================
-- == Command: scan current page
-- ===========================================================================
command.define{
	name = "Security: Scan Current Page",
	run = _wrap_with_debug("command_scan_current_page", function()
		local page_name = "(unknown)"
		if type(editor) == "table" and type(editor.getCurrentPage) == "function" then
			page_name = editor.getCurrentPage()
		end
		generate_reports(page_name)
		if type(editor) == "table" and type(editor.navigate) == "function" then
			editor.navigate("scan:page:" .. page_name)
		elseif type(editor) == "table" and type(editor.flashNotification) == "function" then
			editor.flashNotification("Scan complete for " .. page_name, "info")
		end
	end)
}

-- ===========================================================================
-- == Command: scan all children pages of current page
-- ===========================================================================
-- ===========================================================================
-- == Scan Children Pages of Current Page
-- ===========================================================================
command.define{
	name = "Security: Scan Children Pages",
	run = _wrap_with_debug("command_scan_children_pages", function()
		if type(editor) ~= "table" or type(editor.getCurrentPage) ~= "function" then
			return
		end
		local current_page = editor.getCurrentPage()
		if not current_page or current_page == "" then
			return
		end
    -- get all child pages using index query
		local children_pages = query[[
      from index.tag "page"
      where _.name:find("^" .. current_page .. "/")
    ]]
		local summary = {}
		for _, child in ipairs(children_pages) do
			local page_name = child.name
			local report = generate_reports(page_name)
      -- store summary
			local page_score = string.match(report, "(%d+)%s*%%") or 0
			table.insert(summary, {
				page = page_name,
				score = page_score
			})
		end
    -- store children summary in report cache
		mls.cache.ttl.CacheManager.set("children_summary:" .. current_page, summary)

    -- navigate to virtual page summary
		if type(editor.navigate) == "function" then
			editor.navigate("scan:" .. current_page .. ":children")
		elseif type(editor.flashNotification) == "function" then
			editor.flashNotification("Scan complete for children of " .. current_page, "info")
		end
	end)
}
```

## Changelog

* 2026-01-23:
  * feat: add code quality widget
* 2026-01-20
  * feat: improve link to page
  * chore: improve performance implementing cache system

## Community

[Silverbullet forum](https://community.silverbullet.md/t/risk-audit/3562)



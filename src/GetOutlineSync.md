---
author: claude
description: Two-way sync between SilverBullet and GetOutline (documents + images)
pageDecoration.prefix: "🛎️ "
tags: meta
name: "Library/Malys/GetOutlineSync"
---
# Outline-SilverBullet Sync

Space Lua plug that syncs a SilverBullet folder with GetOutline collections.

## What it does
- **Both directions** — pull (Outline → SB), push (SB → Outline), or full bidirectional sync with conflict detection.
- **All files or one file** — sync the whole folder or just the current page.
- **Images** — pulls Outline attachments into the space; pushes local images back to Outline (best-effort, see caveat).
- **API key** — read from `config` (see CONFIG below).
- **Father folder** — every synced page lives under one configurable SB folder.
- **Collections** — choose which Outline collections to sync (or all).

## Mapping & change detection
Each synced page stores sync state in its frontmatter — do not edit by hand:
- `outlineId` — Outline document id
- `outlineCollectionId` — owning collection
- `outlineRev` — Outline `updatedAt` at last sync (remote-change detector)
- `outlineHash` — hash of local body at last sync (local-change detector)

Page path = `<folder>/<collection>/<title>`. A new page placed under `<folder>/<collection>/…`
(no `outlineId`) is created in that collection on push.

## Conflict rule (bidirectional)
- remote changed only → pull
- local changed only → push
- both changed → **no overwrite**; remote copy saved as `… (conflict <rev>)` + notification
- neither → skip

## Commands (Cmd/Ctrl-Shift-P → "Outline:")
- **Outline: Sync All** — bidirectional, whole folder
- **Outline: Pull All** — Outline → SB only
- **Outline: Push All** — SB → Outline only
- **Outline: Sync Current Page** — bidirectional, just this page

## Image push caveat
Pull (download) is reliable. Push uploads a multipart body through the server proxy; binary
fidelity depends on your Outline storage backend. If an upload fails the local link is kept and
a warning is flashed — text sync still completes.

## CONFIG (add to CONFIG.md)
````
```space-lua
config.set("outline", {
  apiKey   = "ol_api_xxxxxxxxxxxxxxxxxxxx",   -- Outline API token
  baseUrl  = "https://app.getoutline.com",    -- no trailing /api, no trailing slash
  folder   = "Outline",                        -- SilverBullet father folder
  collections = {},                            -- {} = all, else {"Engineering","Docs"} names or ids
})
```
````

---
## Source
```space-lua
-- ===== Outline ⇄ SilverBullet sync =====

local outline = {}

----------------------------------------------------------------------
-- debug trace (uses mls.debug from Malys Utilities)
----------------------------------------------------------------------
LOG_ENABLE = true
if library ~= nil and (mls == nil or mls.debug == nil) then
  library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
end

local TRACE = {}
local function dbg(...)
  local parts = {}
  for _, v in ipairs({ ... }) do parts[#parts + 1] = tostring(v) end
  local line = table.concat(parts, " ")
  TRACE[#TRACE + 1] = line
  if LOG_ENABLE and mls and type(mls.debug) == "function" then
    mls.debug(line, "outline")
  end
end

----------------------------------------------------------------------
-- config / http
----------------------------------------------------------------------
local function cfg()
  local c = config.get("outline")
  if not c or not c.apiKey or c.apiKey == "" then
    error("outline config missing: set config.outline (apiKey, baseUrl, folder)")
  end
  c.baseUrl = (c.baseUrl or "https://app.getoutline.com"):gsub("/+$", "")
  c.folder  = (c.folder or "Outline"):gsub("/+$", "")
  c.collections = c.collections or {}
  return c
end

-- POST <base>/api/<method> with JSON body, returns parsed body table
-- net.proxyFetch sends/returns the body as a raw string -> stringify request,
-- parse response with JSON.
local function api(c, method, params)
  local resp = net.proxyFetch(c.baseUrl .. "/api/" .. method, {
    method = "POST",
    headers = {
      ["Authorization"] = "Bearer " .. c.apiKey,
      ["Content-Type"]  = "application/json",
      ["Accept"]        = "application/json",
    },
    body = js.window.JSON.stringify(js.tojs(params or {})),
  })
  local body = resp.body
  if type(body) == "string" then
    body = js.tolua(js.window.JSON.parse(body))
  end
  -- proxyFetch resp.ok is true even on HTTP 401/403; trust Outline's own fields
  if not resp.ok or (body and body.ok == false) then
    error("Outline " .. method .. " failed: HTTP " ..
      tostring((body and body.status) or resp.status) ..
      " " .. tostring(body and body.message or ""))
  end
  return body
end

-- paginate any list endpoint that returns {data=..., pagination=...}
local function apiList(c, method, params)
  local out, offset, limit = {}, 0, 100
  while true do
    local p = {}
    for k, v in pairs(params or {}) do p[k] = v end
    p.limit, p.offset = limit, offset
    local r = api(c, method, p)
    local data = r.data or {}
    for _, item in ipairs(data) do out[#out + 1] = item end
    if #data < limit then break end
    offset = offset + limit
  end
  return out
end

----------------------------------------------------------------------
-- frontmatter helpers (preserve unknown keys)
----------------------------------------------------------------------
-- returns fmRaw (text inside ---), body
local function splitFM(text)
  local fm, body = text:match("^%-%-%-\n(.-)\n%-%-%-\n?(.*)$")
  if fm then return fm, body end
  return "", text
end

local function fmGet(fm, key)
  return fm:match("\n" .. key .. ":%s*(.-)\n", 1) or fm:match("^" .. key .. ":%s*(.-)\n")
end

local function fmSet(fm, key, value)
  value = tostring(value)
  local line = key .. ": " .. value
  if fm == "" then return line end
  if fm:match("\n" .. key .. ":") or fm:match("^" .. key .. ":") then
    -- replace existing line
    fm = "\n" .. fm .. "\n"
    fm = tostring(fm:gsub("\n" .. key .. ":[^\n]*\n", "\n" .. line .. "\n", 1))
    return fm:sub(2, #fm - 1)
  end
  return fm .. "\n" .. line
end

local function rebuild(fm, body)
  if fm == "" then return body end
  return "---\n" .. fm .. "\n---\n" .. body
end

-- djb2 hash of body for local-change detection
local function hash(s)
  s = tostring(s)   -- s may be a JS-string userdata from :gsub/:match
  local h = 5381
  for i = 1, #s do
    h = (h * 33 + s:byte(i)) % 4294967296
  end
  return h
end

----------------------------------------------------------------------
-- name / path helpers
----------------------------------------------------------------------
-- Accented chars -> ASCII. WARNING: this SB build's gsub matches a pattern char
-- by (codepoint & 0xFF), so any key with codepoint > 255 collides with an ASCII
-- byte (e.g. œ=U+0153 -> 0x53 'S'). Keep ONLY Latin-1 (<=255) keys here.
local ACCENTS = {
  ["à"]="a",["â"]="a",["ä"]="a",["á"]="a",["ã"]="a",["å"]="a",["æ"]="ae",
  ["ç"]="c",["ñ"]="n",
  ["è"]="e",["é"]="e",["ê"]="e",["ë"]="e",
  ["ì"]="i",["í"]="i",["î"]="i",["ï"]="i",
  ["ò"]="o",["ó"]="o",["ô"]="o",["ö"]="o",["õ"]="o",
  ["ù"]="u",["ú"]="u",["û"]="u",["ü"]="u",
  ["ý"]="y",["ÿ"]="y",
  ["À"]="A",["Â"]="A",["Ä"]="A",["Á"]="A",["Ã"]="A",["Æ"]="AE",
  ["Ç"]="C",["Ñ"]="N",
  ["È"]="E",["É"]="E",["Ê"]="E",["Ë"]="E",
  ["Ì"]="I",["Í"]="I",["Î"]="I",["Ï"]="I",
  ["Ò"]="O",["Ó"]="O",["Ô"]="O",["Ö"]="O",["Õ"]="O",
  ["Ù"]="U",["Ú"]="U",["Û"]="U",["Ü"]="U",
}

-- NOTE: in this SB build string:gsub returns a JS-string userdata, so chaining
-- (:gsub(...):gsub(...)) breaks on the 2nd call. Coerce with tostring between.
-- ASCII-only segment: fold accents, then non-alphanumeric -> '-', collapse, trim.
local function sanitize(name)
  name = tostring(name or "untitled")
  for k, v in pairs(ACCENTS) do name = tostring(name:gsub(k, v)) end
  name = tostring(name:lower())                -- lower-case (after accent fold)
  name = tostring(name:gsub("[^%w%-_]", "-"))  -- space + special chars -> dash
  name = tostring(name:gsub("%-+", "-"))       -- collapse repeats
  name = tostring(name:gsub("^%-+", ""))       -- trim leading
  name = tostring(name:gsub("%-+$", ""))       -- trim trailing
  if name == "" then name = "untitled" end
  return name
end

-- nested path including ancestor titles (doc.pathSegs set by fetchRemoteDocs)
local function docPagePath(c, collectionName, doc)
  local segs = doc.pathSegs
  if not segs or #segs == 0 then segs = { sanitize(doc.title) } end
  return c.folder .. "/" .. sanitize(collectionName) .. "/" .. table.concat(segs, "/")
end

local function attDir(c) return c.folder .. "/images" end

local function extFromCT(ct)
  ct = tostring((ct or ""):lower())
  if ct:find("png") then return "png" end
  if ct:find("jpeg") or ct:find("jpg") then return "jpg" end
  if ct:find("gif") then return "gif" end
  if ct:find("webp") then return "webp" end
  if ct:find("svg") then return "svg" end
  return "bin"
end

local function ctFromExt(path)
  local e = tostring((path:match("%.([%w]+)$") or ""):lower())
  if e == "png" then return "image/png" end
  if e == "jpg" or e == "jpeg" then return "image/jpeg" end
  if e == "gif" then return "image/gif" end
  if e == "webp" then return "image/webp" end
  if e == "svg" then return "image/svg+xml" end
  return "application/octet-stream"
end

----------------------------------------------------------------------
-- images: pull (Outline attachment -> local) ; rewrite links
----------------------------------------------------------------------
-- download Outline attachment by id, save locally, return local path
local function pullAttachment(c, id)
  local resp = net.proxyFetch(c.baseUrl .. "/api/attachments.redirect?id=" .. id, {
    method = "GET",
    headers = { ["Authorization"] = "Bearer " .. c.apiKey },
  })
  if not resp.ok then error("attachment download failed: " .. tostring(resp.status)) end
  local ct = resp.headers["content-type"] or resp.headers["Content-Type"]
  local path = attDir(c) .. "/" .. sanitize(id) .. "." .. extFromCT(ct)
  space.writeFile(path, resp.body)
  return path
end

-- rewrite every Outline attachment ref in text to a local attachment path
local function pullImages(c, text)
  return tostring((tostring(text):gsub("(!%[.-%])%((.-)%)", function(alt, url)
    url = tostring(url)
    -- Outline forms: "/api/attachments.redirect?id=UUID" (+ optional ' "=WxH"'),
    -- or "/attachments/UUID". Strip any title/size suffix via the id capture.
    local id = url:match("attachments.-id=([%w%-]+)") or url:match("/attachments/([%w%-]+)")
    if not id then return alt .. "(" .. url .. ")" end
    local ok, localPath = pcall(pullAttachment, c, id)
    if ok then return alt .. "(/" .. localPath .. ")" end   -- leading / = space-root absolute
    dbg("IMG FAIL id=" .. id .. " err=" .. tostring(localPath))
    return alt .. "(" .. url .. ")"
  end)))
end

-- convert Outline container directives (":::info\n…\n:::") to SB blockquote
-- admonitions ("> **info** Info\n> …"). Type kept as-is (lower-cased).
local function convertAdmonitions(text)
  return tostring((tostring(text):gsub(":::([%w]+)[^\n]*\n(.-)\n:::", function(t, inner)
    t = tostring(t):lower()
    local title = tostring(t:sub(1, 1):upper()) .. tostring(t:sub(2))
    inner = tostring(inner)
    inner = tostring(inner:gsub("^[\r\n]+", ""))   -- trim leading blank lines
    inner = tostring(inner:gsub("[%s\r\n]+$", "")) -- trim trailing whitespace
    local lines = { "> **" .. t .. "** " .. title }
    for line in (inner .. "\n"):gmatch("(.-)\n") do
      lines[#lines + 1] = "> " .. line
    end
    return table.concat(lines, "\n")
  end)))
end

-- full pull-side body transform: admonitions + image rewrite
local function pullBody(c, text)
  local out = pullImages(c, convertAdmonitions(text or ""))
  out = tostring(out:gsub("[\\%s]+$", "\n"))   -- drop Outline's trailing "\" / blank lines
  return out
end

-- upload a local attachment to Outline, return outline redirect ref or nil
local function pushAttachment(c, localPath, documentId)
  -- links are space-root absolute ("/work/.../images/x.png"); space.readFile
  -- wants a path without the leading slash.
  local readPath = tostring(tostring(localPath):gsub("^/", ""))
  local fname = readPath:match("[^/]+$")
  local ok, bytes = pcall(space.readFile, readPath)
  if not ok then return nil end
  local size = (type(bytes) == "string") and #bytes or (bytes.length or 0)
  local meta = api(c, "attachments.create", {
    name = fname,
    contentType = ctFromExt(readPath),
    size = size,
    documentId = documentId,
  })
  -- presigned/proxy upload (best-effort multipart)
  local up = meta.data
  local boundary = "----sboutline" .. tostring(hash(readPath))
  local parts = {}
  for k, v in pairs(up.form or {}) do
    parts[#parts + 1] = "--" .. boundary .. "\r\nContent-Disposition: form-data; name=\"" ..
      tostring(k) .. "\"\r\n\r\n" .. tostring(v) .. "\r\n"
  end
  parts[#parts + 1] = "--" .. boundary ..
    "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" ..
    fname .. "\"\r\nContent-Type: " .. ctFromExt(readPath) .. "\r\n\r\n"
  local head = table.concat(parts)
  local resp = net.proxyFetch(tostring(up.uploadUrl), {
    method = "POST",
    headers = { ["Content-Type"] = "multipart/form-data; boundary=" .. boundary },
    body = head .. tostring(bytes) .. "\r\n--" .. boundary .. "--\r\n",
  })
  if not resp.ok then return nil end
  return "/api/attachments.redirect?id=" .. tostring(up.attachment.id)
end

-- rewrite local image refs to Outline refs (best-effort)
local function pushImages(c, text, documentId)
  return tostring((tostring(text):gsub("(!%[.-%])%((.-)%)", function(alt, path)
    path = tostring(path)
    if path:find("^https?://") or path:find("attachments%.redirect") then
      return alt .. "(" .. path .. ")"
    end
    local ok, ref = pcall(pushAttachment, c, path, documentId)
    if ok and ref then return alt .. "(" .. c.baseUrl .. ref .. ")" end
    editor.flashNotification("Image push failed, kept local: " .. path, "error")
    return alt .. "(" .. path .. ")"
  end)))
end

----------------------------------------------------------------------
-- collection resolution
----------------------------------------------------------------------
-- returns { {id=, name=}, ... } limited to config.collections (or all)
local function resolveCollections(c)
  local all = apiList(c, "collections.list", {})
  dbg("collections.list returned", #all, "collection(s):")
  for _, col in ipairs(all) do
    dbg("  - name=[" .. tostring(col.name) .. "] id=" .. tostring(col.id) ..
      " urlId=" .. tostring(col.urlId))
  end
  dbg("config.collections wanted:", table.concat(c.collections, ", "))
  if #c.collections == 0 then
    local out = {}
    for _, col in ipairs(all) do out[#out + 1] = { id = tostring(col.id), name = tostring(col.name) } end
    return out
  end
  local wanted, out = {}, {}
  for _, w in ipairs(c.collections) do
    wanted[w] = true
    -- also accept the URL slug's trailing urlId (e.g. "securite-uFzOTiywlG")
    local urlId = w:match("%-([%w]+)$")
    if urlId then wanted[urlId] = true end
  end
  for _, col in ipairs(all) do
    if wanted[col.id] or wanted[col.name] or wanted[col.urlId] then
      out[#out + 1] = { id = tostring(col.id), name = tostring(col.name) }
    end
  end
  dbg("resolved", #out, "collection(s) after filter")
  return out
end

local function collectionNameById(cols, id)
  for _, col in ipairs(cols) do if col.id == id then return col.name end end
  return "_unknown"
end

----------------------------------------------------------------------
-- index local pages: outlineId -> {name, fm, body}
----------------------------------------------------------------------
local function indexLocal(c)
  local byId, underFolder = {}, {}
  for _, pg in ipairs(space.listPages()) do
    if pg.name:sub(1, #c.folder + 1) == c.folder .. "/" then
      local text = space.readPage(pg.name)
      local fm, body = splitFM(text)
      local id = fmGet(fm, "outlineId")
      local rec = { name = pg.name, fm = fm, body = body, id = id }
      underFolder[#underFolder + 1] = rec
      if id then byId[id] = rec end
    end
  end
  return byId, underFolder
end

----------------------------------------------------------------------
-- core: pull one Outline doc into SB
----------------------------------------------------------------------
local function pullDoc(c, cols, doc, existing)
  local colName = collectionNameById(cols, doc.collectionId)
  local body = pullBody(c, doc.text or "")
  local fm = existing and existing.fm or ""
  fm = fmSet(fm, "outlineId", doc.id)
  fm = fmSet(fm, "outlineCollectionId", doc.collectionId)
  fm = fmSet(fm, "outlineRev", doc.updatedAt)
  fm = fmSet(fm, "outlineHash", hash(body))
  -- bulk pull (doc.pathSegs set) -> canonical no-space path; migrate if renamed.
  -- syncCurrent (no pathSegs) -> keep the page where it is.
  local name = docPagePath(c, colName, doc)
  if existing and not doc.pathSegs then name = existing.name end
  space.writePage(name, rebuild(fm, body))
  if existing and existing.name ~= name then
    pcall(space.deletePage, existing.name)   -- old (e.g. spaced) location removed
  end
  return name
end

-- core: push one SB page to Outline (create or update)
local function pushPage(c, cols, rec)
  local id = rec.id
  if id then
    local body = pushImages(c, rec.body, id)
    local r = api(c, "documents.update", {
      id = id, title = rec.name:match("[^/]+$"), text = body,
    })
    local fm = fmSet(rec.fm, "outlineRev", r.data.updatedAt)
    fm = fmSet(fm, "outlineHash", hash(body))
    space.writePage(rec.name, rebuild(fm, body))
  else
    -- new page: collection = first path segment under folder
    local rel = rec.name:sub(#c.folder + 2)
    local colSeg = rel:match("^([^/]+)/")
    local colId
    for _, col in ipairs(cols) do
      if sanitize(col.name) == colSeg then colId = col.id break end
    end
    if not colId then
      editor.flashNotification("No collection for " .. rec.name .. " (need <folder>/<collection>/…)", "error")
      return
    end
    local body = pushImages(c, rec.body, nil)
    local r = api(c, "documents.create", {
      title = rec.name:match("[^/]+$"), text = body, collectionId = colId, publish = true,
    })
    local fm = fmSet(rec.fm, "outlineId", r.data.id)
    fm = fmSet(fm, "outlineCollectionId", colId)
    fm = fmSet(fm, "outlineRev", r.data.updatedAt)
    fm = fmSet(fm, "outlineHash", hash(body))
    space.writePage(rec.name, rebuild(fm, body))
  end
end

----------------------------------------------------------------------
-- orchestrators
----------------------------------------------------------------------
-- js.tolua leaves scalar leaves as JS userdata; copy only the scalar fields we
-- need, coerced to native Lua strings (tostring is safe on Lua/userdata strings).
-- Avoids touching nested JS objects (user, collaborators, …) which throw on tostring.
local function cleanDoc(full)
  local pid = full.parentDocumentId
  return {
    id           = tostring(full.id),
    title        = tostring(full.title or "untitled"),
    text         = full.text and tostring(full.text) or "",
    updatedAt    = tostring(full.updatedAt),
    collectionId = tostring(full.collectionId),
    parentDocumentId = (pid and tostring(pid) ~= "") and tostring(pid) or nil,
  }
end

-- fetch all remote docs across selected collections.
-- Outline nests docs via parentDocumentId; compute each doc's ancestry chain
-- of titles so children map to nested SB pages (<folder>/<col>/<parent>/<child>).
local function fetchRemoteDocs(c, cols)
  local docs, byId = {}, {}
  for _, col in ipairs(cols) do
    local list = apiList(c, "documents.list", { collectionId = col.id })
    dbg("collection [" .. tostring(col.name) .. "] documents.list:", #list, "doc(s)")
    for i, d in ipairs(list) do
      -- documents.list returns metadata; pull full text
      local ok, err = pcall(function()
        local full = cleanDoc(api(c, "documents.info", { id = d.id }).data)
        docs[#docs + 1] = full
        byId[full.id] = full
      end)
      if not ok then
        dbg("DOC FAIL i=" .. i .. " id=" .. tostring(d.id) .. " err=" .. tostring(err))
      end
    end
  end
  -- build nested path segments (ancestors first) for every doc
  for pi, d in ipairs(docs) do
    local ok, err = pcall(function()
      local segs, cur, guard = {}, d, 0
      while cur and guard < 50 do
        table.insert(segs, 1, sanitize(cur.title))
        cur = (cur.parentDocumentId and cur.parentDocumentId ~= "") and byId[cur.parentDocumentId] or nil
        guard = guard + 1
      end
      d.pathSegs = segs
    end)
    if not ok then
      dbg("PATH FAIL pi=" .. pi .. " id=" .. tostring(d.id) ..
        " title=" .. tostring(d.title) .. " err=" .. tostring(err))
      d.pathSegs = { sanitize(tostring(d.title)) }
    end
  end
  dbg("fetchRemoteDocs done:", #docs, "doc(s)")
  return docs
end

-- direction: "pull" | "push" | "sync"
function outline.runAll(direction)
  local c = cfg()
  TRACE = {}
  dbg("== Outline " .. direction .. " ==", os.date())
  dbg("baseUrl:", c.baseUrl, " folder:", c.folder)
  editor.flashNotification("Outline " .. direction .. "…", "info")
  local cols = resolveCollections(c)
  local byId, underFolder = indexLocal(c)
  local remote = fetchRemoteDocs(c, cols)
  dbg("remote docs fetched:", #remote)
  local seen, n = {}, 0

  for di, doc in ipairs(remote) do
    local pok, perr = pcall(function()
    seen[doc.id] = true
    local local_ = byId[doc.id]
    if direction == "pull" then
      pullDoc(c, cols, doc, local_); n = n + 1
    elseif direction == "push" then
      if local_ then pushPage(c, cols, local_); n = n + 1 end
    else -- sync
      if not local_ then
        pullDoc(c, cols, doc, nil); n = n + 1
      else
        local remoteChanged = (fmGet(local_.fm, "outlineRev") ~= doc.updatedAt)
        local localChanged  = (tostring(hash(local_.body)) ~= (fmGet(local_.fm, "outlineHash") or ""))
        if remoteChanged and localChanged then
          local cp = local_.name .. " (conflict " .. (doc.updatedAt or "?"):gsub("[:.]", "-") .. ")"
          space.writePage(cp, pullBody(c, doc.text or ""))
          editor.flashNotification("Conflict: " .. local_.name .. " → kept local, remote saved as copy", "error")
        elseif remoteChanged then
          pullDoc(c, cols, doc, local_); n = n + 1
        elseif localChanged then
          pushPage(c, cols, local_); n = n + 1
        end
      end
    end
    end)
    if not pok then
      dbg("PULL FAIL di=" .. di .. " id=" .. tostring(doc.id) ..
        " title=" .. tostring(doc.title) ..
        " segs=" .. tostring(doc.pathSegs and #doc.pathSegs) ..
        " err=" .. tostring(perr))
    end
  end

  -- new local pages (no outlineId) -> push on sync/push
  if direction ~= "pull" then
    for _, rec in ipairs(underFolder) do
      if not rec.id and not rec.name:match("/_attachments/") then
        pushPage(c, cols, rec); n = n + 1
      end
    end
  end

  dbg("== done:", n, "doc(s) written ==")
  if LOG_ENABLE and mls and type(mls.debug) == "function" then
    mls.debug(table.concat(TRACE, "\n"), "outline")
  end
  editor.flashNotification("Outline " .. direction .. " done (" .. n .. " docs)", "info")
end

-- single current page, bidirectional
function outline.syncCurrent()
  local c = cfg()
  local name = editor.getCurrentPage()
  if name:sub(1, #c.folder + 1) ~= c.folder .. "/" then
    editor.flashNotification("Page not under '" .. c.folder .. "/'", "error")
    return
  end
  local cols = resolveCollections(c)
  local fm, body = splitFM(space.readPage(name))
  local rec = { name = name, fm = fm, body = body, id = fmGet(fm, "outlineId") }
  if not rec.id then
    pushPage(c, cols, rec)
    editor.flashNotification("Created in Outline", "info")
    return
  end
  local doc = cleanDoc(api(c, "documents.info", { id = rec.id }).data)
  local remoteChanged = (fmGet(fm, "outlineRev") ~= doc.updatedAt)
  local localChanged  = (tostring(hash(body)) ~= (fmGet(fm, "outlineHash") or ""))
  if remoteChanged and localChanged then
    local cp = name .. " (conflict " .. (doc.updatedAt or "?"):gsub("[:.]", "-") .. ")"
    space.writePage(cp, pullBody(c, doc.text or ""))
    editor.flashNotification("Conflict — remote saved as copy, local kept", "error")
  elseif remoteChanged then
    pullDoc(c, cols, doc, rec)
    editor.flashNotification("Pulled from Outline", "info")
  elseif localChanged then
    pushPage(c, cols, rec)
    editor.flashNotification("Pushed to Outline", "info")
  else
    editor.flashNotification("Already in sync", "info")
  end
end

----------------------------------------------------------------------
-- commands
----------------------------------------------------------------------
--command.define { name = "Outline: Sync All",          run = function() outline.runAll("sync") end }
command.define { name = "Outline: Pull All",          run = function() outline.runAll("pull") end }
--command.define { name = "Outline: Push All",          run = function() outline.runAll("push") end }
command.define { name = "Outline: Sync Current Page", run = function() outline.syncCurrent() end }
```

## Changelog

* 2026-06-13:
  * feat: debug trace via `mls.debug`
  * fix: resolve collections by URL slug / urlId, not only id/name

## Community

[Silverbullet forum](https://community.silverbullet.md/)
